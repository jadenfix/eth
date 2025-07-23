"""
T1-A: Real-time Ethereum ingestion pipeline
Functional test: Complete ingestion from source to storage
"""

import pytest
import asyncio
import time
import json
from tests.e2e.helpers.gcp import GCPTestUtils, CHAIN_EVENTS_SCHEMA

@pytest.mark.e2e
@pytest.mark.tier1
class TestRealTimeIngestion:
    """Test real-time Ethereum data ingestion pipeline"""
    
    def test_pubsub_to_bigquery_pipeline(self, gcp_env, pubsub_publisher, bigquery_client, sample_chain_event, clean_test_data):
        """
        T1-A: End-to-end ingestion pipeline test
        
        Flow:
        1. Setup Pub/Sub topic and BigQuery destination
        2. Publish Ethereum event to Pub/Sub
        3. Simulate Dataflow processing
        4. Verify data appears correctly in BigQuery
        5. Validate data transformation and enrichment
        """
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        # 1. Setup pipeline infrastructure
        test_dataset = f"{gcp_env.test_prefix}_realtime_ingestion"
        test_table = "ethereum_events"
        test_topic = f"{gcp_env.test_prefix}_ethereum_raw"
        test_subscription = f"{gcp_env.test_prefix}_ethereum_processor"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, CHAIN_EVENTS_SCHEMA)
        gcp_utils.pubsub_create_topic(test_topic)
        gcp_utils.pubsub_create_subscription(test_topic, test_subscription)
        
        # 2. Create realistic Ethereum event
        ethereum_event = {
            "block_number": 18500000,
            "transaction_hash": "0xa1b2c3d4e5f6789012345678901234567890123456789012345678901234567890",
            "from_address": "0x742F35Cc6E8C9f4E31a52c6b0d4b4Eb0Df4E7EAe",
            "to_address": "0xA0b86a33E6E4A3b9d60bAE5e3cD3A8B2C5d8E5F2",
            "value": "1500000000000000000",  # 1.5 ETH
            "gas_used": 21000,
            "gas_price": "20000000000",  # 20 Gwei
            "timestamp": int(time.time()),
            "event_type": "transfer",
            "contract_address": None,
            "input_data": "0x",
            "logs": json.dumps([]),
            "status": 1,
            "fixture_id": "T1_A_realtime"
        }
        
        # 3. Publish to Pub/Sub
        message_id = gcp_utils.pubsub_publish(test_topic, ethereum_event, {
            "source": "ethereum_node",
            "chain": "mainnet",
            "pipeline_stage": "raw_ingestion"
        })
        
        assert message_id, "Should receive message ID from Pub/Sub"
        
        # 4. Simulate message processing (in real system, Dataflow would do this)
        # Pull message from subscription
        messages = gcp_utils.pubsub_pull_messages(test_subscription, max_messages=1)
        assert len(messages) == 1, "Should receive the published message"
        
        received_message = messages[0]
        assert received_message["data"] == ethereum_event, "Received data should match published data"
        
        # Simulate data enrichment (what Dataflow would do)
        enriched_event = ethereum_event.copy()
        enriched_event.update({
            "block_timestamp": ethereum_event["timestamp"],
            "eth_value": float(ethereum_event["value"]) / 1e18,  # Convert wei to ETH
            "gas_cost_eth": (int(ethereum_event["gas_used"]) * int(ethereum_event["gas_price"])) / 1e18,
            "processed_timestamp": int(time.time()),
            "pipeline_version": "v3-alpha"
        })
        
        # 5. Insert enriched data to BigQuery
        gcp_utils.bq_insert_rows(test_dataset, test_table, [enriched_event])
        
        # 6. Verify data in BigQuery
        query = f"""
        SELECT *
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id = 'T1_A_realtime'
        """
        
        results = gcp_utils.bq_query(query)
        assert len(results) == 1, "Should have exactly one result"
        
        result = results[0]
        assert result["transaction_hash"] == ethereum_event["transaction_hash"]
        assert result["from_address"] == ethereum_event["from_address"]
        assert result["to_address"] == ethereum_event["to_address"]
        assert float(result["eth_value"]) == 1.5, "Should convert wei to ETH correctly"
        assert "pipeline_version" in result, "Should include pipeline metadata"
        
        print("✅ T1-A: Real-time ingestion pipeline test passed")
    
    def test_high_volume_ingestion(self, gcp_env, pubsub_publisher, bigquery_client, clean_test_data):
        """Test ingestion pipeline under load"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_volume_test"
        test_table = "high_volume_events"
        test_topic = f"{gcp_env.test_prefix}_volume_raw"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, CHAIN_EVENTS_SCHEMA)
        gcp_utils.pubsub_create_topic(test_topic)
        
        # Generate batch of events
        batch_size = 100
        events = []
        
        for i in range(batch_size):
            event = {
                "block_number": 18500000 + i,
                "transaction_hash": f"0x{i:064x}",
                "from_address": f"0x{(i*2):040x}",
                "to_address": f"0x{(i*2+1):040x}",
                "value": str(1000000000000000000 + i),  # 1+ ETH
                "gas_used": 21000 + (i % 1000),
                "gas_price": str(20000000000 + (i % 10000000000)),
                "timestamp": int(time.time()) + i,
                "event_type": "transfer",
                "fixture_id": "T1_A_volume"
            }
            events.append(event)
        
        # Publish batch to Pub/Sub
        published_count = 0
        for event in events:
            message_id = gcp_utils.pubsub_publish(test_topic, event)
            if message_id:
                published_count += 1
        
        assert published_count == batch_size, f"Should publish all {batch_size} events"
        
        # Simulate batch processing to BigQuery
        gcp_utils.bq_insert_rows(test_dataset, test_table, events)
        
        # Verify all data arrived
        query = f"""
        SELECT COUNT(*) as count
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id = 'T1_A_volume'
        """
        
        results = gcp_utils.bq_query(query)
        assert results[0]["count"] == batch_size, f"Should have {batch_size} records in BigQuery"
        
        print(f"✅ T1-A: High volume ingestion test passed ({batch_size} events)")
    
    def test_data_validation_and_filtering(self, gcp_env, pubsub_publisher, bigquery_client, clean_test_data):
        """Test data validation and filtering in ingestion pipeline"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_validation"
        test_table = "validated_events"
        test_topic = f"{gcp_env.test_prefix}_validation_raw"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, CHAIN_EVENTS_SCHEMA)
        gcp_utils.pubsub_create_topic(test_topic)
        
        # Create mix of valid and invalid events
        test_events = [
            # Valid event
            {
                "block_number": 18500000,
                "transaction_hash": "0xvalid123456789012345678901234567890123456789012345678901234567890",
                "from_address": "0x742F35Cc6E8C9f4E31a52c6b0d4b4Eb0Df4E7EAe",
                "to_address": "0xA0b86a33E6E4A3b9d60bAE5e3cD3A8B2C5d8E5F2",
                "value": "1000000000000000000",
                "gas_used": 21000,
                "timestamp": int(time.time()),
                "event_type": "transfer",
                "fixture_id": "T1_A_validation_valid"
            },
            # Invalid event - bad address format
            {
                "block_number": 18500001,
                "transaction_hash": "0xinvalid12345678901234567890123456789012345678901234567890123456789",
                "from_address": "invalid_address",
                "to_address": "0xA0b86a33E6E4A3b9d60bAE5e3cD3A8B2C5d8E5F2",
                "value": "1000000000000000000",
                "gas_used": 21000,
                "timestamp": int(time.time()),
                "event_type": "transfer",
                "fixture_id": "T1_A_validation_invalid"
            },
            # Invalid event - negative value
            {
                "block_number": 18500002,
                "transaction_hash": "0xbadvalue12345678901234567890123456789012345678901234567890123456",
                "from_address": "0x742F35Cc6E8C9f4E31a52c6b0d4b4Eb0Df4E7EAe",
                "to_address": "0xA0b86a33E6E4A3b9d60bAE5e3cD3A8B2C5d8E5F2",
                "value": "-1000000000000000000",
                "gas_used": 21000,
                "timestamp": int(time.time()),
                "event_type": "transfer",
                "fixture_id": "T1_A_validation_invalid"
            }
        ]
        
        # Publish all events
        for event in test_events:
            gcp_utils.pubsub_publish(test_topic, event)
        
        # Simulate validation logic (would be in Dataflow)
        valid_events = []
        for event in test_events:
            # Basic validation rules
            is_valid = True
            
            # Check address format
            if not (event["from_address"].startswith("0x") and len(event["from_address"]) == 42):
                is_valid = False
            if not (event["to_address"].startswith("0x") and len(event["to_address"]) == 42):
                is_valid = False
            
            # Check value is positive
            try:
                value = int(event["value"])
                if value < 0:
                    is_valid = False
            except ValueError:
                is_valid = False
            
            if is_valid:
                valid_events.append(event)
        
        # Insert only valid events to BigQuery
        if valid_events:
            gcp_utils.bq_insert_rows(test_dataset, test_table, valid_events)
        
        # Verify only valid events made it through
        query = f"""
        SELECT *
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id LIKE 'T1_A_validation_%'
        """
        
        results = gcp_utils.bq_query(query)
        
        # Should only have the valid event
        assert len(results) == 1, "Should only have valid events in BigQuery"
        assert results[0]["fixture_id"] == "T1_A_validation_valid"
        assert results[0]["from_address"].startswith("0x")
        assert int(results[0]["value"]) > 0
        
        print("✅ T1-A: Data validation and filtering test passed")
    
    @pytest.mark.asyncio
    async def test_streaming_ingestion_latency(self, gcp_env, pubsub_publisher, bigquery_client, clean_test_data):
        """Test ingestion latency for streaming data"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_latency"
        test_table = "latency_events"
        test_topic = f"{gcp_env.test_prefix}_latency_raw"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, CHAIN_EVENTS_SCHEMA)
        gcp_utils.pubsub_create_topic(test_topic)
        
        # Track timing
        events_with_timing = []
        
        # Send events with timestamps
        for i in range(10):
            publish_time = time.time()
            event = {
                "block_number": 18500000 + i,
                "transaction_hash": f"0xlatency{i:056x}",
                "from_address": f"0x{i:040x}",
                "to_address": f"0x{(i+1):040x}",
                "value": "1000000000000000000",
                "gas_used": 21000,
                "timestamp": int(publish_time),
                "event_type": "transfer",
                "publish_timestamp": publish_time,
                "fixture_id": "T1_A_latency"
            }
            
            message_id = gcp_utils.pubsub_publish(test_topic, event)
            
            if message_id:
                events_with_timing.append({
                    "event": event,
                    "publish_time": publish_time,
                    "message_id": message_id
                })
            
            # Small delay between events
            await asyncio.sleep(0.1)
        
        # Simulate processing with recorded times
        processing_time = time.time()
        processed_events = []
        
        for item in events_with_timing:
            event = item["event"]
            event["processing_timestamp"] = processing_time
            event["latency_ms"] = (processing_time - item["publish_time"]) * 1000
            processed_events.append(event)
        
        # Insert to BigQuery
        gcp_utils.bq_insert_rows(test_dataset, test_table, processed_events)
        
        # Analyze latency
        query = f"""
        SELECT 
            AVG(latency_ms) as avg_latency_ms,
            MAX(latency_ms) as max_latency_ms,
            MIN(latency_ms) as min_latency_ms,
            COUNT(*) as event_count
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id = 'T1_A_latency'
        """
        
        results = gcp_utils.bq_query(query)
        latency_stats = results[0]
        
        assert latency_stats["event_count"] == 10, "Should process all events"
        assert latency_stats["avg_latency_ms"] < 5000, "Average latency should be under 5 seconds"
        assert latency_stats["max_latency_ms"] < 10000, "Max latency should be under 10 seconds"
        
        print(f"✅ T1-A: Streaming latency test passed (avg: {latency_stats['avg_latency_ms']:.2f}ms)")
    
    def test_duplicate_detection(self, gcp_env, pubsub_publisher, bigquery_client, clean_test_data):
        """Test duplicate event detection and handling"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_dedup"
        test_table = "dedup_events"
        test_topic = f"{gcp_env.test_prefix}_dedup_raw"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, CHAIN_EVENTS_SCHEMA)
        gcp_utils.pubsub_create_topic(test_topic)
        
        # Create the same event multiple times (simulate duplicate sends)
        base_event = {
            "block_number": 18500000,
            "transaction_hash": "0xduplicate123456789012345678901234567890123456789012345678901234567890",
            "from_address": "0x742F35Cc6E8C9f4E31a52c6b0d4b4Eb0Df4E7EAe",
            "to_address": "0xA0b86a33E6E4A3b9d60bAE5e3cD3A8B2C5d8E5F2",
            "value": "1000000000000000000",
            "gas_used": 21000,
            "timestamp": int(time.time()),
            "event_type": "transfer",
            "fixture_id": "T1_A_dedup"
        }
        
        # Send the same event 3 times
        message_ids = []
        for i in range(3):
            duplicate_event = base_event.copy()
            duplicate_event["send_attempt"] = i + 1
            
            message_id = gcp_utils.pubsub_publish(test_topic, duplicate_event)
            message_ids.append(message_id)
        
        assert len(message_ids) == 3, "Should publish all duplicate events"
        
        # Simulate deduplication logic (would be in Dataflow)
        # In real system, this would use transaction_hash + block_number as unique key
        seen_events = set()
        unique_events = []
        
        for i in range(3):
            event = base_event.copy()
            event["send_attempt"] = i + 1
            
            # Create unique key for deduplication
            unique_key = f"{event['transaction_hash']}_{event['block_number']}"
            
            if unique_key not in seen_events:
                seen_events.add(unique_key)
                unique_events.append(event)
        
        # Insert only unique events
        gcp_utils.bq_insert_rows(test_dataset, test_table, unique_events)
        
        # Verify only one event made it through
        query = f"""
        SELECT COUNT(*) as count
        FROM `{gcp_env.project_id}.{test_dataset}.{test_table}`
        WHERE fixture_id = 'T1_A_dedup'
        """
        
        results = gcp_utils.bq_query(query)
        assert results[0]["count"] == 1, "Should only have one unique event after deduplication"
        
        print("✅ T1-A: Duplicate detection test passed")
