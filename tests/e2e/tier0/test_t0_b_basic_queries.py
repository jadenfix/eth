"""
T0-B: Query BigQuery → returns valid JSON
Demo-blocking test: Basic query functionality works
"""

import pytest
import json
from tests.e2e.helpers.gcp import GCPTestUtils

@pytest.mark.e2e
@pytest.mark.tier0
class TestBigQueryQueries:
    """Test basic BigQuery query functionality"""
    
    def test_simple_bigquery_query(self, gcp_env, bigquery_client, clean_test_data):
        """
        T0-B: Basic BigQuery query test
        
        Flow:
        1. Insert known test data
        2. Query for that data
        3. Verify JSON structure and content
        4. Validate response format
        """
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        # 1. Setup test data
        test_dataset = f"{gcp_env.test_prefix}_query_test"
        test_table = "chain_events"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, {
            "fields": [
                {"name": "id", "type": "STRING"},
                {"name": "value", "type": "INTEGER"},
                {"name": "metadata", "type": "STRING"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        test_data = [
            {"id": "test_1", "value": 100, "metadata": '{"type": "test"}', "fixture_id": "T0_B_query"},
            {"id": "test_2", "value": 200, "metadata": '{"type": "test"}', "fixture_id": "T0_B_query"},
            {"id": "test_3", "value": 300, "metadata": '{"type": "other"}', "fixture_id": "T0_B_query"}
        ]
        
        gcp_utils.bq_insert_rows(test_dataset, test_table, test_data)
        
        # 2. Query the data
        query = f"""
        SELECT id, value, metadata
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id = 'T0_B_query'
        ORDER BY value
        """
        
        results = gcp_utils.bq_query(query)
        
        # 3. Verify JSON structure
        assert isinstance(results, list), "Results should be a list"
        assert len(results) == 3, "Should have 3 results"
        
        # 4. Validate response format
        for result in results:
            assert "id" in result, "Each result should have 'id' field"
            assert "value" in result, "Each result should have 'value' field"
            assert "metadata" in result, "Each result should have 'metadata' field"
            
            # Validate JSON in metadata field
            metadata = json.loads(result["metadata"])
            assert "type" in metadata, "Metadata should be valid JSON with 'type' field"
        
        # Verify specific values
        assert results[0]["value"] == 100
        assert results[1]["value"] == 200
        assert results[2]["value"] == 300
        
        print("✅ T0-B: Basic BigQuery query test passed")
    
    def test_aggregated_query(self, gcp_env, bigquery_client, clean_test_data):
        """Test aggregated BigQuery queries"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_query_test"
        test_table = "transactions"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, {
            "fields": [
                {"name": "address", "type": "STRING"},
                {"name": "amount", "type": "FLOAT"},
                {"name": "category", "type": "STRING"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        # Insert test data
        test_data = [
            {"address": "0xA", "amount": 1.5, "category": "DeFi", "fixture_id": "T0_B_agg"},
            {"address": "0xA", "amount": 2.5, "category": "DeFi", "fixture_id": "T0_B_agg"},
            {"address": "0xB", "amount": 10.0, "category": "NFT", "fixture_id": "T0_B_agg"},
            {"address": "0xC", "amount": 0.1, "category": "DeFi", "fixture_id": "T0_B_agg"}
        ]
        
        gcp_utils.bq_insert_rows(test_dataset, test_table, test_data)
        
        # Query aggregated data
        query = f"""
        SELECT 
            category,
            COUNT(*) as transaction_count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id = 'T0_B_agg'
        GROUP BY category
        ORDER BY total_amount DESC
        """
        
        results = gcp_utils.bq_query(query)
        
        # Validate aggregated results
        assert len(results) == 2, "Should have 2 categories"
        
        # Check DeFi category (should be first due to ORDER BY)
        defi_result = next(r for r in results if r["category"] == "DeFi")
        assert defi_result["transaction_count"] == 3
        assert abs(defi_result["total_amount"] - 4.1) < 0.01
        assert abs(defi_result["avg_amount"] - 1.37) < 0.01
        
        # Check NFT category
        nft_result = next(r for r in results if r["category"] == "NFT")
        assert nft_result["transaction_count"] == 1
        assert nft_result["total_amount"] == 10.0
        assert nft_result["avg_amount"] == 10.0
        
        print("✅ T0-B: Aggregated query test passed")
    
    def test_query_with_filters(self, gcp_env, bigquery_client, clean_test_data):
        """Test BigQuery queries with complex filters"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_query_test"
        test_table = "filtered_events"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, {
            "fields": [
                {"name": "timestamp", "type": "INTEGER"},
                {"name": "event_type", "type": "STRING"},
                {"name": "risk_score", "type": "FLOAT"},
                {"name": "amount", "type": "STRING"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        # Insert test data with various scenarios
        test_data = [
            {"timestamp": 1698000000, "event_type": "transfer", "risk_score": 0.1, "amount": "1000000", "fixture_id": "T0_B_filter"},
            {"timestamp": 1698000100, "event_type": "swap", "risk_score": 0.8, "amount": "5000000", "fixture_id": "T0_B_filter"},
            {"timestamp": 1698000200, "event_type": "transfer", "risk_score": 0.3, "amount": "500000", "fixture_id": "T0_B_filter"},
            {"timestamp": 1698000300, "event_type": "mint", "risk_score": 0.9, "amount": "10000000", "fixture_id": "T0_B_filter"}
        ]
        
        gcp_utils.bq_insert_rows(test_dataset, test_table, test_data)
        
        # Query with complex filters
        query = f"""
        SELECT *
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id = 'T0_B_filter'
          AND risk_score > 0.5
          AND CAST(amount AS INT64) > 1000000
          AND event_type IN ('swap', 'mint')
        ORDER BY timestamp
        """
        
        results = gcp_utils.bq_query(query)
        
        # Should only return swap and mint events with high risk and large amounts
        assert len(results) == 2, "Should have 2 high-risk, large-amount events"
        assert results[0]["event_type"] == "swap"
        assert results[1]["event_type"] == "mint"
        assert all(float(r["risk_score"]) > 0.5 for r in results)
        
        print("✅ T0-B: Complex filter query test passed")
