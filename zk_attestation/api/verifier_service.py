"""
ZK Signal Verifier API Service
Provides REST endpoints for zero-knowledge proof verification of ML model attestations
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import json
import asyncio
import subprocess
import os
import hashlib
from datetime import datetime, timedelta
from web3 import Web3
from web3.middleware import geth_poa_middleware
import redis
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ZK Signal Verifier API",
    description="Zero-knowledge proof verification for ML model attestations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for caching
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Web3 connection (configure for your network)
w3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URL', 'http://localhost:8545')))
if w3.is_connected():
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Contract addresses (set via environment variables)
VERIFIER_CONTRACT_ADDRESS = os.getenv('VERIFIER_CONTRACT_ADDRESS')
MODEL_VERIFIER_ADDRESS = os.getenv('MODEL_VERIFIER_ADDRESS')
SIGNAL_VERIFIER_ADDRESS = os.getenv('SIGNAL_VERIFIER_ADDRESS')

# Pydantic models
class ProofRequest(BaseModel):
    proof_type: str = Field(..., description="Type of proof: 'model' or 'signal'")
    model_data: Optional[Dict[str, Any]] = Field(None, description="Model parameters for model proofs")
    signal_data: Optional[Dict[str, Any]] = Field(None, description="Signal data for signal proofs")

class ModelProofData(BaseModel):
    weights: List[float] = Field(..., min_items=16, max_items=16)
    version: int = Field(..., ge=1)
    timestamp: int = Field(...)

class SignalProofData(BaseModel):
    signal_type: int = Field(..., ge=1, le=10)
    confidence: int = Field(..., ge=0, le=100)
    model_hash: str = Field(...)
    timestamp: int = Field(...)

class ProofResponse(BaseModel):
    proof: Dict[str, Any]
    public_signals: List[str]
    verification_result: bool
    proof_hash: str
    generated_at: datetime

class VerificationRequest(BaseModel):
    proof: Dict[str, Any]
    public_signals: List[str]
    proof_type: str

class AttestationRequest(BaseModel):
    proof: Dict[str, Any]
    public_signals: List[str]
    proof_type: str
    contract_params: Dict[str, Any]

# Service classes
class ZKProofService:
    def __init__(self):
        self.prover_path = "./zk_attestation/prover"
        self.node_cmd = "node"
    
    async def generate_proof(self, proof_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate zero-knowledge proof using Node.js prover"""
        try:
            # Create temporary input file
            input_file = f"/tmp/zk_input_{proof_type}_{os.getpid()}.json"
            with open(input_file, 'w') as f:
                json.dump(data, f)
            
            # Run proof generation
            cmd = [
                self.node_cmd,
                f"{self.prover_path}/generate_proof.js",
                proof_type,
                input_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"Proof generation failed: {result.stderr}")
                raise HTTPException(status_code=500, detail=f"Proof generation failed: {result.stderr}")
            
            # Parse output
            proof_data = json.loads(result.stdout)
            
            # Clean up temp file
            os.unlink(input_file)
            
            return proof_data
            
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="Proof generation timeout")
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Invalid proof output format")
        except Exception as e:
            logger.error(f"Proof generation error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Proof generation error: {str(e)}")
    
    async def verify_proof(self, proof: Dict, public_signals: List[str], proof_type: str) -> bool:
        """Verify zero-knowledge proof"""
        try:
            # Create temporary files
            proof_file = f"/tmp/zk_proof_{proof_type}_{os.getpid()}.json"
            signals_file = f"/tmp/zk_signals_{proof_type}_{os.getpid()}.json"
            
            with open(proof_file, 'w') as f:
                json.dump(proof, f)
            
            with open(signals_file, 'w') as f:
                json.dump(public_signals, f)
            
            # Run verification
            cmd = [
                self.node_cmd,
                f"{self.prover_path}/verify_proof.js",
                proof_type,
                proof_file,
                signals_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Clean up temp files
            os.unlink(proof_file)
            os.unlink(signals_file)
            
            if result.returncode != 0:
                logger.error(f"Proof verification failed: {result.stderr}")
                return False
            
            return "true" in result.stdout.lower()
            
        except Exception as e:
            logger.error(f"Proof verification error: {str(e)}")
            return False

class ContractService:
    def __init__(self):
        self.w3 = w3
        self.verifier_contract = None
        if VERIFIER_CONTRACT_ADDRESS and self.w3.is_connected():
            self.load_contract()
    
    def load_contract(self):
        """Load the verifier contract"""
        try:
            # Load ABI (you would need to provide the actual ABI)
            with open('./contracts/ZKSignalVerifier.json', 'r') as f:
                contract_data = json.load(f)
                abi = contract_data['abi']
            
            self.verifier_contract = self.w3.eth.contract(
                address=VERIFIER_CONTRACT_ADDRESS,
                abi=abi
            )
        except Exception as e:
            logger.error(f"Failed to load contract: {str(e)}")
    
    async def attest_on_chain(self, proof_data: Dict, proof_type: str, params: Dict) -> str:
        """Submit attestation to blockchain"""
        if not self.verifier_contract:
            raise HTTPException(status_code=503, detail="Contract not available")
        
        try:
            # Format proof for contract
            formatted_proof = self.format_proof_for_contract(proof_data['proof'])
            
            # Build transaction
            if proof_type == "model":
                function = self.verifier_contract.functions.attestModel(
                    formatted_proof['a'],
                    formatted_proof['b'],
                    formatted_proof['c'],
                    params['model_hash'],
                    params['version'],
                    params['timestamp']
                )
            elif proof_type == "signal":
                function = self.verifier_contract.functions.attestSignal(
                    formatted_proof['a'],
                    formatted_proof['b'],
                    formatted_proof['c'],
                    params['signal_hash'],
                    params['model_hash'],
                    params['signal_type'],
                    params['timestamp']
                )
            else:
                raise ValueError(f"Unknown proof type: {proof_type}")
            
            # Build and send transaction (you would need proper account management)
            account = self.w3.eth.account.from_key(os.getenv('PRIVATE_KEY'))
            txn = function.build_transaction({
                'from': account.address,
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(account.address),
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"On-chain attestation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"On-chain attestation failed: {str(e)}")
    
    def format_proof_for_contract(self, proof: Dict) -> Dict:
        """Format proof for smart contract submission"""
        return {
            'a': [proof['pi_a'][0], proof['pi_a'][1]],
            'b': [[proof['pi_b'][0][1], proof['pi_b'][0][0]], [proof['pi_b'][1][1], proof['pi_b'][1][0]]],
            'c': [proof['pi_c'][0], proof['pi_c'][1]]
        }

# Service instances
proof_service = ZKProofService()
contract_service = ContractService()

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "proof_generation": True,
            "blockchain": w3.is_connected() if w3 else False,
            "redis": redis_client.ping() if redis_client else False
        }
    }

@app.post("/generate-proof", response_model=ProofResponse)
async def generate_proof(request: ProofRequest):
    """Generate zero-knowledge proof for model or signal"""
    try:
        # Validate request
        if request.proof_type not in ["model", "signal", "composite"]:
            raise HTTPException(status_code=400, detail="Invalid proof type")
        
        # Check cache first
        cache_key = f"proof:{request.proof_type}:{hash(str(request.dict()))}"
        cached_result = redis_client.get(cache_key)
        if cached_result:
            return ProofResponse(**json.loads(cached_result))
        
        # Generate proof
        if request.proof_type == "model":
            if not request.model_data:
                raise HTTPException(status_code=400, detail="Model data required for model proofs")
            proof_data = await proof_service.generate_proof("model", request.model_data)
        
        elif request.proof_type == "signal":
            if not request.signal_data:
                raise HTTPException(status_code=400, detail="Signal data required for signal proofs")
            proof_data = await proof_service.generate_proof("signal", request.signal_data)
        
        elif request.proof_type == "composite":
            if not request.model_data or not request.signal_data:
                raise HTTPException(status_code=400, detail="Both model and signal data required for composite proofs")
            proof_data = await proof_service.generate_proof("composite", {
                "model_data": request.model_data,
                "signal_data": request.signal_data
            })
        
        # Verify proof
        verification_result = await proof_service.verify_proof(
            proof_data['proof'],
            proof_data['publicSignals'],
            request.proof_type
        )
        
        # Create response
        proof_hash = hashlib.sha256(json.dumps(proof_data, sort_keys=True).encode()).hexdigest()
        
        response = ProofResponse(
            proof=proof_data['proof'],
            public_signals=proof_data['publicSignals'],
            verification_result=verification_result,
            proof_hash=proof_hash,
            generated_at=datetime.utcnow()
        )
        
        # Cache result for 1 hour
        redis_client.setex(cache_key, 3600, response.json())
        
        return response
        
    except Exception as e:
        logger.error(f"Proof generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-proof")
async def verify_proof(request: VerificationRequest):
    """Verify a zero-knowledge proof"""
    try:
        result = await proof_service.verify_proof(
            request.proof,
            request.public_signals,
            request.proof_type
        )
        
        return {
            "verified": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Proof verification failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/attest-on-chain")
async def attest_on_chain(request: AttestationRequest):
    """Submit proof attestation to blockchain"""
    try:
        # Verify proof first
        verification_result = await proof_service.verify_proof(
            request.proof,
            request.public_signals,
            request.proof_type
        )
        
        if not verification_result:
            raise HTTPException(status_code=400, detail="Invalid proof")
        
        # Submit to blockchain
        tx_hash = await contract_service.attest_on_chain(
            {"proof": request.proof, "publicSignals": request.public_signals},
            request.proof_type,
            request.contract_params
        )
        
        return {
            "transaction_hash": tx_hash,
            "verified": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"On-chain attestation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/proofs/{proof_hash}")
async def get_proof(proof_hash: str):
    """Retrieve proof by hash"""
    try:
        # Search cache for proof
        for key in redis_client.scan_iter(match=f"proof:*"):
            cached_data = redis_client.get(key)
            if cached_data:
                proof_data = json.loads(cached_data)
                if proof_data.get('proof_hash') == proof_hash:
                    return proof_data
        
        raise HTTPException(status_code=404, detail="Proof not found")
        
    except Exception as e:
        logger.error(f"Proof retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    try:
        # Count cached proofs by type
        proof_counts = {"model": 0, "signal": 0, "composite": 0}
        
        for key in redis_client.scan_iter(match="proof:*"):
            key_parts = key.split(":")
            if len(key_parts) >= 2:
                proof_type = key_parts[1]
                if proof_type in proof_counts:
                    proof_counts[proof_type] += 1
        
        return {
            "total_proofs_generated": sum(proof_counts.values()),
            "proofs_by_type": proof_counts,
            "blockchain_connected": w3.is_connected() if w3 else False,
            "cache_status": "connected" if redis_client.ping() else "disconnected"
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
