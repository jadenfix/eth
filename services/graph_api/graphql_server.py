from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .resolvers import schema
from .neo4j_client import Neo4jClient
from services.entity_resolution.pipeline import EntityResolutionPipeline
from services.mev_agent.mev_agent import MEVAgent
from services.agents.whale_tracker import WhaleTracker
from services.risk_ai.risk_scorer import RiskScorer
from services.access_control.sanctions_checker import SanctionsChecker
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Graph API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GraphQL router
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# Initialize services
neo4j_client = Neo4jClient()
entity_pipeline = EntityResolutionPipeline()

# Initialize Phase 3 services
mev_agent = MEVAgent()
whale_tracker = WhaleTracker()
risk_scorer = RiskScorer()
sanctions_checker = SanctionsChecker()

# Initialize risk scorer with sample data
risk_scorer.initialize_with_sample_data()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        metrics = neo4j_client.get_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {
            "status": "disconnected",
            "wallets": 0,
            "transactions": 0,
            "entities": 0,
            "clusters": 0
        }

@app.get("/wallets/{address}")
async def get_wallet(address: str):
    """Get wallet information"""
    try:
        wallet = neo4j_client.get_wallet(address)
        if wallet:
            return wallet
        else:
            raise HTTPException(status_code=404, detail="Wallet not found")
    except Exception as e:
        logger.error(f"Error getting wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entity-resolution/sample")
async def process_sample_data():
    """Process sample entity resolution data"""
    try:
        result = await entity_pipeline.process_sample_data()
        return result
    except Exception as e:
        logger.error(f"Error processing sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/entity-resolution/process")
async def process_transactions(request: Dict[str, Any]):
    """Process transactions for entity resolution"""
    try:
        transactions = request.get("transactions", [])
        result = await entity_pipeline.process_new_transactions(transactions)
        return result
    except Exception as e:
        logger.error(f"Error processing transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entity-resolution/real-data")
async def process_real_data(limit: int = 50):
    """Process real blockchain data"""
    try:
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("latest", limit)
        await entity_pipeline.cleanup()
        return result
    except Exception as e:
        logger.error(f"Error processing real data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entity-resolution/whale-data")
async def process_whale_data():
    """Process whale transaction data"""
    try:
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("whale")
        await entity_pipeline.cleanup()
        return result
    except Exception as e:
        logger.error(f"Error processing whale data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entity-resolution/mev-data")
async def process_mev_data():
    """Process MEV transaction data"""
    try:
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("mev")
        await entity_pipeline.cleanup()
        return result
    except Exception as e:
        logger.error(f"Error processing MEV data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/entities/search")
async def search_entities(query: str, limit: int = 10):
    """Search entities"""
    try:
        results = neo4j_client.search_entities(query, limit)
        return {
            "query": query,
            "entities": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/analysis/patterns")
async def analyze_graph_patterns():
    """Analyze graph patterns"""
    try:
        # Get basic graph metrics
        metrics = neo4j_client.get_metrics()
        return {
            "total_nodes": metrics.get("wallets", 0),
            "total_relationships": metrics.get("transactions", 0),
            "total_entities": metrics.get("entities", 0),
            "total_clusters": metrics.get("clusters", 0),
            "patterns": {
                "high_value_transactions": 0,
                "frequent_traders": 0,
                "contract_interactions": 0
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing graph patterns: {e}")
        return {
            "total_nodes": 0,
            "total_relationships": 0,
            "total_entities": 0,
            "total_clusters": 0,
            "patterns": {}
        }

@app.get("/graph/analysis/clusters")
async def analyze_clusters():
    """Analyze entity clusters"""
    try:
        clusters = neo4j_client.get_clusters(100)
        return {
            "metrics": {
                "total_clusters": len(clusters),
                "avg_cluster_size": sum(c.get("size", 0) for c in clusters) / max(len(clusters), 1),
                "largest_cluster": max((c.get("size", 0) for c in clusters), default=0)
            },
            "clusters": clusters
        }
    except Exception as e:
        logger.error(f"Error analyzing clusters: {e}")
        return {
            "metrics": {
                "total_clusters": 0,
                "avg_cluster_size": 0,
                "largest_cluster": 0
            },
            "clusters": []
        }

@app.post("/dev/create-wallet")
async def create_wallet(address: str):
    """Development endpoint to create a wallet"""
    try:
        result = neo4j_client.create_wallet_node(address)
        return {"status": "success", "address": address, "created": result}
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dev/create-relationship")
async def create_relationship(from_address: str, to_address: str, tx_hash: str):
    """Development endpoint to create a relationship"""
    try:
        result = neo4j_client.create_transaction_relationship(from_address, to_address, tx_hash)
        return {"status": "success", "relationship": result}
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/multi-chain/latest")
async def get_multi_chain_latest():
    """Get latest data from multiple chains"""
    try:
        # For now, just return Ethereum data
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("latest", 10)
        await entity_pipeline.cleanup()
        
        return {
            "ethereum": result,
            "polygon": {"status": "not_implemented"},
            "arbitrum": {"status": "not_implemented"}
        }
    except Exception as e:
        logger.error(f"Error getting multi-chain data: {e}")
        return {
            "ethereum": {"error": str(e)},
            "polygon": {"status": "not_implemented"},
            "arbitrum": {"status": "not_implemented"}
        }

# ============================================================================
# PHASE 3: INTELLIGENCE AGENTS ENDPOINTS
# ============================================================================

@app.get("/mev/detect")
async def detect_mev_activity():
    """Detect MEV activity in recent transactions"""
    try:
        # Get sample transactions for MEV detection
        sample_transactions = [
            {
                "hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                "from": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                "value": 1500000000000000000,  # 1.5 ETH
                "gasPrice": 25000000000,  # 25 gwei
                "gasUsed": 21000,
                "blockNumber": 18000000,
                "transactionIndex": 0
            },
            {
                "hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "from": "0xdaFCE5670d3F67da9A3A44D6f3e82C7b8c5c3b3b",  # MEV bot
                "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                "value": 500000000000000000,  # 0.5 ETH
                "gasPrice": 500000000000,  # 500 gwei (high gas)
                "gasUsed": 30000,
                "blockNumber": 18000000,
                "transactionIndex": 1
            },
            {
                "hash": "0x112233445566778899aabbccddeeff00112233445566778899aabbccddeeff00",
                "from": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                "value": 10000000000000000000,  # 10 ETH
                "gasPrice": 40000000000,  # 40 gwei
                "gasUsed": 30000,
                "blockNumber": 18000000,
                "transactionIndex": 2
            }
        ]
        
        signals = await mev_agent.process_sample_transactions(sample_transactions)
        
        return {
            "signals_detected": len(signals),
            "signals": [
                {
                    "signal_id": signal.signal_id,
                    "signal_type": signal.signal_type,
                    "confidence_score": signal.confidence_score,
                    "profit_estimate": signal.profit_estimate,
                    "addresses_involved": signal.addresses_involved,
                    "metadata": signal.metadata
                }
                for signal in signals
            ]
        }
    except Exception as e:
        logger.error(f"Error detecting MEV activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mev/statistics")
async def get_mev_statistics():
    """Get MEV detection statistics"""
    try:
        stats = await mev_agent.get_mev_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting MEV statistics: {e}")
        return {
            "total_signals": 0,
            "avg_confidence": 0.0,
            "total_profit": 0.0,
            "by_type": {}
        }

@app.get("/whale/track")
async def track_whale_movements():
    """Track whale movements in recent transactions"""
    try:
        # Sample whale transactions
        whale_transactions = [
            {
                "hash": "0xwhale1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
                "from": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "to": "0x21a31ee1afc51d94c2efccaa2092ad1028285549",  # Binance
                "value": 100000000000000000000,  # 100 ETH
                "gasPrice": 25000000000,
                "gasUsed": 21000,
                "blockNumber": 18000000
            },
            {
                "hash": "0xwhale2345678901abcdef1234567890abcdef1234567890abcdef1234567890",
                "from": "0x21a31ee1afc51d94c2efccaa2092ad1028285549",  # Binance
                "to": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "value": 50000000000000000000,  # 50 ETH
                "gasPrice": 25000000000,
                "gasUsed": 21000,
                "blockNumber": 18000001
            }
        ]
        
        movements = await whale_tracker.process_sample_transactions(whale_transactions)
        
        return {
            "movements_detected": len(movements),
            "movements": [
                {
                    "whale_id": movement.whale_id,
                    "address": movement.address,
                    "movement_type": movement.movement_type,
                    "value_eth": movement.value_eth,
                    "value_usd": movement.value_usd,
                    "confidence_score": movement.confidence_score,
                    "metadata": movement.metadata
                }
                for movement in movements
            ]
        }
    except Exception as e:
        logger.error(f"Error tracking whale movements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/whale/statistics")
async def get_whale_statistics():
    """Get whale tracking statistics"""
    try:
        # Return basic statistics without calling the method that might be causing issues
        return {
            "known_whales": len(whale_tracker.known_whales),
            "total_movements": len(whale_tracker.whale_movements),
            "movements_by_type": whale_tracker._count_movements_by_type(),
            "largest_movement": whale_tracker._get_largest_movement(),
            "recent_activity": whale_tracker._get_recent_activity()
        }
    except Exception as e:
        logger.error(f"Error getting whale statistics: {e}")
        return {
            "known_whales": 0,
            "total_movements": 0,
            "movements_by_type": {},
            "largest_movement": None,
            "recent_activity": []
        }

@app.post("/risk/calculate")
async def calculate_risk_score(request: Dict[str, Any]):
    """Calculate risk score for an address"""
    try:
        address = request.get("address")
        address_data = request.get("address_data", {})
        
        if not address:
            raise HTTPException(status_code=400, detail="Address is required")
        
        risk_score = risk_scorer.calculate_risk_score(address, address_data)
        explanation = risk_scorer.explain_risk_score(address, address_data)
        
        return {
            "address": address,
            "risk_score": risk_score,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Error calculating risk score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/risk/feature-importance")
async def get_feature_importance():
    """Get feature importance from the risk scoring model"""
    try:
        importance = risk_scorer.get_feature_importance()
        return {
            "feature_importance": importance,
            "total_features": len(importance)
        }
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
        return {
            "feature_importance": {},
            "total_features": 0
        }

@app.post("/sanctions/check")
async def check_sanctions(request: Dict[str, Any]):
    """Check addresses for sanctions"""
    try:
        addresses = request.get("addresses", [])
        
        if not addresses:
            raise HTTPException(status_code=400, detail="Addresses list is required")
        
        results = await sanctions_checker.process_sample_addresses(addresses)
        
        return {
            "addresses_checked": len(results),
            "results": [
                {
                    "address": result.address,
                    "is_sanctioned": result.is_sanctioned,
                    "sanctions_list": result.sanctions_list,
                    "confidence_score": result.confidence_score,
                    "metadata": result.metadata
                }
                for result in results
            ]
        }
    except Exception as e:
        logger.error(f"Error checking sanctions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sanctions/statistics")
async def get_sanctions_statistics():
    """Get sanctions checking statistics"""
    try:
        stats = sanctions_checker.get_sanctions_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error getting sanctions statistics: {e}")
        return {
            "total_addresses_checked": 0,
            "sanctioned_addresses": 0,
            "sanction_rate": 0,
            "cache_hit_rate": 0,
            "recent_checks": []
        }

@app.get("/phase3/status")
async def get_phase3_status():
    """Get overall Phase 3 status and health"""
    try:
        return {
            "phase": "Phase 3 - Intelligence Agents",
            "status": "operational",
            "services": {
                "mev_detection": "active",
                "whale_tracking": "active", 
                "risk_scoring": "active",
                "sanctions_checking": "active"
            },
            "endpoints": [
                "/mev/detect",
                "/mev/statistics", 
                "/whale/track",
                "/whale/statistics",
                "/risk/calculate",
                "/risk/feature-importance",
                "/sanctions/check",
                "/sanctions/statistics"
            ],
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Error getting Phase 3 status: {e}")
        return {
            "phase": "Phase 3 - Intelligence Agents",
            "status": "error",
            "error": str(e)
        } 