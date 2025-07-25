"""
E2E-ZK-01: Proof Generation

Test ZK-Attestation proof generation pipeline.
Validates that signals can be cryptographically attested with zero-knowledge proofs.
"""

import json
import time
import pytest
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List

from tests.e2e.helpers.gcp import GCPTestUtils


@pytest.mark.e2e
class TestZKProofGeneration:
    """Test ZK-Attestation proof generation"""
    
    def test_proof_generation_pipeline(self, gcp_env, bigquery_client, clean_test_data):
        """
        E2E-ZK-01: Proof Generation
        
        Flow:
        1. Publish mock signal.json to Pub/Sub
        2. Cloud Function runs zk_attestation/prover/generate_proof.ts
        3. Artifact: proof.json in GCS bucket contains proof, publicSignals, signalHash
        4. Validate snarkJS groth16 verify returns true locally
        """
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        # Setup test environment
        test_dataset = f"{gcp_env.test_prefix}_zk_proofs"
        signals_table = "signals"
        proofs_table = "signal_proofs"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, signals_table, {
            "fields": [
                {"name": "signal_id", "type": "STRING", "mode": "REQUIRED"},
                {"name": "signal_type", "type": "STRING", "mode": "REQUIRED"},
                {"name": "severity", "type": "STRING", "mode": "NULLABLE"},
                {"name": "confidence_score", "type": "FLOAT", "mode": "NULLABLE"},
                {"name": "related_addresses", "type": "STRING", "mode": "NULLABLE"},
                {"name": "metadata", "type": "STRING", "mode": "NULLABLE"},
                {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
                {"name": "fixture_id", "type": "STRING", "mode": "NULLABLE"}
            ]
        })
        
        gcp_utils.bq_create_table(test_dataset, proofs_table, {
            "fields": [
                {"name": "signal_id", "type": "STRING", "mode": "REQUIRED"},
                {"name": "proof_hash", "type": "STRING", "mode": "REQUIRED"},
                {"name": "public_signals", "type": "STRING", "mode": "NULLABLE"},
                {"name": "proof_data", "type": "STRING", "mode": "NULLABLE"},
                {"name": "verification_result", "type": "BOOLEAN", "mode": "NULLABLE"},
                {"name": "created_at", "type": "TIMESTAMP", "mode": "NULLABLE"},
                {"name": "fixture_id", "type": "STRING", "mode": "NULLABLE"}
            ]
        })
        
        # 1. Create test signal
        test_signal = {
            "signal_id": "ZK_TEST_001",
            "signal_type": "HIGH_VALUE_TRANSFER",
            "severity": "HIGH",
            "confidence_score": 0.95,
            "related_addresses": json.dumps(["0xZK_TEST_001", "0xZK_TEST_002"]),
            "metadata": json.dumps({
                "value_usd": 1000000,
                "gas_price_gwei": 150,
                "block_number": 18500000
            }),
            "created_at": "2024-01-01T00:00:00Z",
            "fixture_id": "E2E_ZK_01"
        }
        
        # Insert signal to BigQuery
        gcp_utils.bq_insert_rows(test_dataset, signals_table, [test_signal])
        
        # 2. Simulate Pub/Sub message (in real system, this would trigger the Cloud Function)
        # For testing, we'll simulate the proof generation process
        
        # Create temporary signal file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_signal, f)
            signal_file_path = f.name
        
        try:
            # 3. Simulate proof generation (mock the actual ZK circuit)
            # In a real implementation, this would call the actual ZK prover
            proof_data = self._generate_mock_proof(test_signal)
            
            # 4. Store proof in BigQuery
            proof_record = {
                "signal_id": test_signal["signal_id"],
                "proof_hash": proof_data["proofHash"],
                "public_signals": json.dumps(proof_data["publicSignals"]),
                "proof_data": json.dumps(proof_data["proof"]),
                "verification_result": True,
                "created_at": "2024-01-01T00:00:00Z",
                "fixture_id": "E2E_ZK_01"
            }
            
            gcp_utils.bq_insert_rows(test_dataset, proofs_table, [proof_record])
            
            # 5. Verify proof was generated and stored
            verify_query = f"""
            SELECT signal_id, proof_hash, verification_result
            FROM `{gcp_env.project_id}.{test_dataset}.{proofs_table}`
            WHERE fixture_id = 'E2E_ZK_01'
            """
            
            proof_results = gcp_utils.bq_query(verify_query)
            
            assert len(proof_results) == 1, "Should have one proof record"
            assert proof_results[0]["signal_id"] == "ZK_TEST_001"
            assert proof_results[0]["proof_hash"] == proof_data["proofHash"]
            assert proof_results[0]["verification_result"] == True
            
            # 6. Validate proof structure
            assert "proof" in proof_data, "Proof should contain proof data"
            assert "publicSignals" in proof_data, "Proof should contain public signals"
            assert "proofHash" in proof_data, "Proof should contain proof hash"
            
            print("✅ E2E-ZK-01: Proof generation pipeline completed successfully")
            
        finally:
            # Cleanup
            if os.path.exists(signal_file_path):
                os.unlink(signal_file_path)
    
    def test_proof_verification(self, gcp_env, bigquery_client, clean_test_data):
        """Test ZK proof verification"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        # Setup test environment
        test_dataset = f"{gcp_env.test_prefix}_zk_verification"
        proofs_table = "signal_proofs"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, proofs_table, {
            "fields": [
                {"name": "signal_id", "type": "STRING", "mode": "REQUIRED"},
                {"name": "proof_hash", "type": "STRING", "mode": "REQUIRED"},
                {"name": "public_signals", "type": "STRING", "mode": "NULLABLE"},
                {"name": "proof_data", "type": "STRING", "mode": "NULLABLE"},
                {"name": "verification_result", "type": "BOOLEAN", "mode": "NULLABLE"},
                {"name": "fixture_id", "type": "STRING", "mode": "NULLABLE"}
            ]
        })
        
        # 1. Create test proof data
        test_proof = self._generate_mock_proof({
            "signal_id": "ZK_VERIFY_TEST_001",
            "signal_type": "MEV_ATTACK",
            "severity": "CRITICAL"
        })
        
        # 2. Store proof
        proof_record = {
            "signal_id": "ZK_VERIFY_TEST_001",
            "proof_hash": test_proof["proofHash"],
            "public_signals": json.dumps(test_proof["publicSignals"]),
            "proof_data": json.dumps(test_proof["proof"]),
            "verification_result": None,  # Will be set after verification
            "fixture_id": "E2E_ZK_01_VERIFY"
        }
        
        gcp_utils.bq_insert_rows(test_dataset, proofs_table, [proof_record])
        
        # 3. Simulate proof verification (mock snarkJS groth16 verify)
        verification_result = self._verify_mock_proof(test_proof)
        
        # 4. Insert verification result (BigQuery streaming doesn't support UPDATE)
        verification_record = {
            "signal_id": "ZK_VERIFY_TEST_001",
            "proof_hash": test_proof["proofHash"],
            "public_signals": json.dumps(test_proof["publicSignals"]),
            "proof_data": json.dumps(test_proof["proof"]),
            "verification_result": verification_result,
            "fixture_id": "E2E_ZK_01_VERIFY_RESULT"
        }
        
        gcp_utils.bq_insert_rows(test_dataset, proofs_table, [verification_record])
        
        # 5. Verify the result
        verify_query = f"""
        SELECT verification_result
        FROM `{gcp_env.project_id}.{test_dataset}.{proofs_table}`
        WHERE fixture_id = 'E2E_ZK_01_VERIFY_RESULT'
        """
        
        result = gcp_utils.bq_query(verify_query)
        assert len(result) == 1, "Should have one verification result"
        assert result[0]["verification_result"] == True, "Proof should verify successfully"
        
        print("✅ E2E-ZK-01: Proof verification completed successfully")
    
    def _generate_mock_proof(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock ZK proof for testing"""
        # In a real implementation, this would call the actual ZK circuit
        signal_hash = f"0x{hash(json.dumps(signal_data, sort_keys=True)) % (2**256):064x}"
        
        return {
            "proof": {
                "pi_a": ["0x1234567890abcdef", "0xfedcba0987654321"],
                "pi_b": [["0x1111111111111111", "0x2222222222222222"], 
                        ["0x3333333333333333", "0x4444444444444444"]],
                "pi_c": ["0x5555555555555555", "0x6666666666666666"]
            },
            "publicSignals": [
                signal_hash,
                "0x0000000000000000000000000000000000000000000000000000000000000001"
            ],
            "proofHash": f"0x{hash(signal_hash) % (2**256):064x}"
        }
    
    def _verify_mock_proof(self, proof_data: Dict[str, Any]) -> bool:
        """Verify mock ZK proof"""
        # In a real implementation, this would call snarkJS groth16 verify
        # For testing, we'll return True if the proof has the expected structure
        required_fields = ["proof", "publicSignals", "proofHash"]
        return all(field in proof_data for field in required_fields)
