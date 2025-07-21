"""
Integration tests that can run without external API keys.
Tests service interactions using mocks and local resources.
"""

import pytest
import asyncio
import json
import os
import tempfile
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from pathlib import Path

# Set test environment
os.environ.update({
    'GOOGLE_CLOUD_PROJECT': 'test-project',
    'ETHEREUM_RPC_URL': 'http://mock-node:8545', 
    'REDIS_URL': 'redis://localhost:6379/15',
    'TEST_MODE': 'true',
    'ELEVENLABS_API_KEY': 'test-key-12345',
    'COINGECKO_API_KEY': 'test-coingecko-key'
})


@pytest.fixture(scope="session")
def test_workspace():
    """Create test workspace directory."""
    with tempfile.TemporaryDirectory(prefix="onchain_test_") as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_blockchain_events():
    """Sample blockchain events for testing."""
    return [
        {
            'block_number': 18500000,
            'transaction_hash': '0x1234567890abcdef' + '0' * 48,
            'from_address': '0xsender123' + '0' * 29,
            'to_address': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',  # Uniswap
            'value_eth': 1.5,
            'value_usd': 3000.0,
            'gas_price_gwei': 50.0,
            'event_name': 'TRANSFER',
            'timestamp': datetime.now().isoformat()
        },
        {
            'block_number': 18500001,
            'transaction_hash': '0xmevbot567890' + '0' * 44,
            'from_address': '0xmevbot456' + '0' * 29,
            'to_address': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
            'value_eth': 10.0,
            'value_usd': 20000.0,
            'gas_price_gwei': 200.0,  # High gas price
            'event_name': 'SWAP', 
            'timestamp': datetime.now().isoformat()
        }
    ]


class TestIngestionToProcessing:
    """Test data flow from ingestion to processing."""
    
    @pytest.mark.asyncio
    async def test_pubsub_message_flow(self, sample_blockchain_events):
        """Test Pub/Sub message publishing and consuming."""
        published_messages = []
        
        # Mock Pub/Sub publisher
        with patch('google.cloud.pubsub_v1.PublisherClient') as mock_pub:
            mock_client = Mock()
            
            def capture_publish(topic, data, **kwargs):
                published_messages.append(json.loads(data.decode('utf-8')))
                return Mock()
            
            mock_client.publish.side_effect = capture_publish
            mock_pub.return_value = mock_client
            
            # Simulate ingestion service
            from services.ethereum_ingester.ethereum_ingester import MessagePublisher
            
            publisher = MessagePublisher()
            
            # Publish test events
            for event in sample_blockchain_events:
                await publisher.publish_event('blockchain-events', event)
            
            # Verify messages were published
            assert len(published_messages) == 2
            assert published_messages[0]['event_name'] == 'TRANSFER'
            assert published_messages[1]['event_name'] == 'SWAP'
    
    @pytest.mark.asyncio
    async def test_agent_message_consumption(self, sample_blockchain_events):
        """Test agent consuming and processing messages."""
        processed_events = []
        
        # Mock MEV agent
        from services.mev_agent.mev_agent import MEVWatchAgent
        
        agent = MEVWatchAgent()
        
        # Mock signal publishing
        async def capture_signal(signal):
            processed_events.append({
                'signal_type': signal.signal_type,
                'confidence': signal.confidence_score,
                'addresses': signal.related_addresses
            })
        
        agent._publish_signal = capture_signal
        
        # Process high-gas event (should trigger MEV detection)
        high_gas_event = sample_blockchain_events[1]
        await agent._analyze_transaction(high_gas_event)
        
        # Verify signal was generated
        assert len(processed_events) >= 1
        signal = processed_events[0]
        assert signal['signal_type'] in ['FRONT_RUNNING', 'HIGH_GAS_ANOMALY']
        assert signal['confidence'] > 0.0


class TestAPIIntegration:
    """Test API service integration."""
    
    def test_rest_api_health_endpoints(self):
        """Test REST API health and status endpoints."""
        from services.dashboard.status_dashboard import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        
        # Test system status
        response = client.get("/system/status")
        assert response.status_code == 200
        data = response.json()
        assert 'overall_status' in data
        assert 'services' in data
        
        # Test recent signals
        response = client.get("/signals/recent?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert 'signals' in data
        assert isinstance(data['signals'], list)
    
    def test_graphql_api_basic_queries(self):
        """Test GraphQL API basic functionality.""" 
        from services.graph_api.graph_api import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test schema introspection
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                types {
                    name
                    kind
                }
            }
        }
        """
        
        response = client.post("/graphql", json={"query": introspection_query})
        assert response.status_code == 200
        
        data = response.json()
        assert 'data' in data
        assert '__schema' in data['data']
        
        # Verify core types exist
        type_names = [t['name'] for t in data['data']['__schema']['types']]
        expected_types = ['Entity', 'Address', 'Transaction', 'Query']
        
        for expected_type in expected_types:
            assert expected_type in type_names
    
    @pytest.mark.asyncio
    async def test_websocket_real_time_updates(self):
        """Test WebSocket real-time data streaming.""" 
        from services.dashboard.status_dashboard import manager
        
        # Mock WebSocket connections
        mock_ws1 = AsyncMock()
        mock_ws2 = AsyncMock()
        
        # Connect clients
        await manager.connect(mock_ws1)
        await manager.connect(mock_ws2)
        
        # Broadcast test data
        test_data = {
            'type': 'signal_update',
            'signal': {
                'signal_id': 'TEST_001',
                'signal_type': 'MEV_ATTACK',
                'severity': 'HIGH',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        await manager.broadcast(test_data)
        
        # Verify all clients received the message
        mock_ws1.send_text.assert_called()
        mock_ws2.send_text.assert_called()
        
        # Verify message content
        sent_message = json.loads(mock_ws1.send_text.call_args[0][0])
        assert sent_message['type'] == 'signal_update'
        assert sent_message['signal']['signal_id'] == 'TEST_001'


class TestDatabaseIntegration:
    """Test database integration without external dependencies."""
    
    @pytest.mark.asyncio
    async def test_entity_resolution_mock_flow(self):
        """Test entity resolution with mocked ML pipeline."""
        # Mock BigQuery
        with patch('google.cloud.bigquery.Client') as mock_bq:
            mock_client = Mock()
            mock_job = Mock()
            mock_job.result.return_value = [
                Mock(address='0xabc123', tx_count=100, total_volume=50.5),
                Mock(address='0xdef456', tx_count=150, total_volume=75.2)
            ]
            mock_client.query.return_value = mock_job
            mock_bq.return_value = mock_client
            
            # Mock Neo4j
            with patch('neo4j.GraphDatabase.driver') as mock_neo4j:
                from services.entity_resolution.pipeline import EntityResolutionPipeline
                
                pipeline = EntityResolutionPipeline()
                
                # Test entity resolution
                result = await pipeline.resolve_entities(['0xabc123', '0xdef456'])
                
                assert 'entity_id' in result
                assert 'addresses' in result
                assert 'confidence' in result
                assert result['confidence'] > 0.0
    
    def test_bigquery_mock_queries(self):
        """Test BigQuery query functionality with mocks."""
        with patch('google.cloud.bigquery.Client') as mock_bq:
            mock_client = Mock()
            
            # Mock query result
            mock_result = [
                {'block_number': 18500000, 'tx_count': 150},
                {'block_number': 18500001, 'tx_count': 143},
                {'block_number': 18500002, 'tx_count': 167}
            ]
            
            mock_job = Mock()
            mock_job.result.return_value = [Mock(**row) for row in mock_result]
            mock_client.query.return_value = mock_job
            mock_bq.return_value = mock_client
            
            # Test database helper
            from services.ingestion.database_helper import BigQueryHelper
            
            helper = BigQueryHelper()
            results = helper.query_recent_blocks(limit=3)
            
            assert len(results) == 3
            assert results[0]['block_number'] == 18500000


class TestSecurityAndCompliance:
    """Test security and compliance features."""
    
    def test_access_control_policy_enforcement(self):
        """Test access control policy evaluation."""
        from services.access_control.audit_sink import PolicyEvaluator
        
        evaluator = PolicyEvaluator()
        
        # Test analyst access to limited data
        result = evaluator.evaluate_access(
            user='analyst@company.com',
            resource='onchain_data.curated_events',
            action='SELECT',
            columns=['transaction_hash', 'block_number'],
            context={'value_usd': 5000}
        )
        
        assert result['allowed'] == True
        
        # Test denied access to sensitive columns
        result = evaluator.evaluate_access(
            user='analyst@company.com',
            resource='onchain_data.sensitive_addresses',
            action='SELECT',
            columns=['entity_name', 'kyc_data'],
            context={}
        )
        
        assert result['allowed'] == False
        assert 'insufficient_permissions' in result['reason']
    
    def test_audit_logging_functionality(self):
        """Test comprehensive audit logging."""
        from services.access_control.audit_sink import AuditLogger
        
        logger = AuditLogger()
        
        # Generate test audit entries
        entries = []
        
        # Successful query
        entries.append(logger.log_access(
            user='analyst@company.com',
            resource='transactions_table',
            action='SELECT',
            result='SUCCESS',
            metadata={'rows_returned': 150}
        ))
        
        # Failed access attempt
        entries.append(logger.log_access(
            user='external@badactor.com',
            resource='sensitive_data',
            action='SELECT', 
            result='DENIED',
            metadata={'reason': 'unauthorized_user'}
        ))
        
        # Verify audit entries structure
        for entry in entries:
            assert 'user' in entry
            assert 'resource' in entry
            assert 'action' in entry
            assert 'result' in entry
            assert 'timestamp' in entry
            assert 'session_id' in entry
    
    def test_data_masking_implementation(self):
        """Test data masking for sensitive information."""
        from services.access_control.audit_sink import DataMasker
        
        masker = DataMasker()
        
        # Test data with mixed sensitive and non-sensitive fields
        test_record = {
            'transaction_hash': '0x123abc456def789',
            'from_address': '0xsender123',
            'to_address': '0xrecipient456',
            'user_email': 'user@example.com',
            'phone_number': '+1-555-123-4567',
            'value_usd': 15000.50
        }
        
        masked_record = masker.mask_sensitive_data(test_record, user_role='analyst')
        
        # Blockchain data should remain unchanged
        assert masked_record['transaction_hash'] == test_record['transaction_hash']
        assert masked_record['from_address'] == test_record['from_address']
        assert masked_record['value_usd'] == test_record['value_usd']
        
        # PII should be masked
        assert masked_record['user_email'] != test_record['user_email']
        assert '***' in masked_record['phone_number']


class TestWorkflowIntegration:
    """Test workflow builder integration."""
    
    def test_dagster_job_definition_loading(self):
        """Test loading Dagster job definitions."""
        from services.workflow_builder.sample_signal import (
            high_value_transfer_monitor,
            suspicious_activity_monitor
        )
        
        # Verify jobs are defined
        assert high_value_transfer_monitor is not None
        assert suspicious_activity_monitor is not None
        
        # Check job has required attributes
        assert hasattr(high_value_transfer_monitor, 'name')
        assert hasattr(high_value_transfer_monitor, 'op_defs')
    
    def test_custom_workflow_creation(self):
        """Test dynamic workflow creation."""
        from services.workflow_builder.sample_signal import build_custom_workflow
        
        # Define custom workflow config
        config = {
            'name': 'large_transfer_detector',
            'ops': {
                'fetch_blockchain_data': {
                    'config': {
                        'query': 'SELECT * FROM transfers WHERE value_usd > 100000',
                        'parameters': {}
                    }
                },
                'detect_anomalies': {
                    'config': {
                        'threshold': 500000,
                        'comparison': 'greater_than', 
                        'metric': 'value_usd'
                    }
                },
                'generate_signal': {
                    'config': {
                        'signal_type': 'WHALE_MOVEMENT',
                        'description': 'Large whale transfer detected',
                        'severity': 'MEDIUM'
                    }
                }
            }
        }
        
        # Build custom workflow
        workflow = build_custom_workflow(config)
        
        assert workflow is not None
        assert workflow.name == 'large_transfer_detector'
    
    @pytest.mark.asyncio
    async def test_workflow_execution_simulation(self):
        """Test workflow execution with mocked components."""
        import pandas as pd
        from unittest.mock import Mock
        from services.workflow_builder.sample_signal import (
            fetch_blockchain_data,
            detect_anomalies,
            generate_signal
        )
        
        # Mock BigQuery resource and data
        mock_bq = Mock()
        mock_context = Mock()
        
        # Mock fetch operation
        mock_context.op_config = {
            'query': 'SELECT * FROM test_table',
            'parameters': {}
        }
        
        test_df = pd.DataFrame([
            {'transaction_hash': '0x1', 'value_usd': 750000},
            {'transaction_hash': '0x2', 'value_usd': 50000},
            {'transaction_hash': '0x3', 'value_usd': 1200000}
        ])
        
        # Mock BigQuery client response
        mock_bq.get_client.return_value.query.return_value.to_dataframe.return_value = test_df
        
        # Test data fetching
        fetched_data = fetch_blockchain_data(mock_context, mock_bq)
        assert len(fetched_data) == 3
        
        # Test anomaly detection
        mock_context.op_config = {
            'threshold': 500000,
            'comparison': 'greater_than',
            'metric': 'value_usd'
        }
        
        anomalies = detect_anomalies(mock_context, fetched_data)
        assert len(anomalies) == 2  # Two values > 500k
        
        # Test signal generation
        mock_context.op_config = {
            'signal_type': 'HIGH_VALUE_TRANSFER',
            'description': 'Large transfer detected',
            'severity': 'HIGH'
        }
        mock_context.run_id = 'test_run_123'
        mock_context.job_name = 'test_workflow'
        
        signal = generate_signal(mock_context, anomalies)
        
        assert signal['signal_type'] == 'HIGH_VALUE_TRANSFER'
        assert signal['severity'] == 'HIGH'
        assert len(signal['related_transactions']) == 2


class TestSystemHealthMonitoring:
    """Test system health and monitoring integration."""
    
    @pytest.mark.asyncio
    async def test_health_check_service_discovery(self):
        """Test health checking of registered services."""
        from services.monitoring.health_service import HealthMonitoringService
        
        service = HealthMonitoringService()
        
        # Mock HTTP responses for services
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {'status': 'healthy', 'version': '1.0.0'}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with service.health_checker:
                # Check a service
                health_result = await service.health_checker.check_http_service(
                    'ethereum-ingester',
                    'http://localhost:8001'
                )
                
                assert health_result.service_name == 'ethereum-ingester'
                assert health_result.status.value == 'healthy'
                assert health_result.response_time_ms > 0
    
    def test_metrics_collection_and_aggregation(self):
        """Test system metrics collection."""
        from services.monitoring.health_service import MetricsCollector
        
        collector = MetricsCollector()
        
        # Collect system metrics
        system_metrics = collector.collect_system_metrics()
        
        # Verify metrics structure
        assert system_metrics.cpu_percent >= 0
        assert system_metrics.memory_percent >= 0
        assert system_metrics.disk_percent >= 0
        assert isinstance(system_metrics.network_io, tuple)
        assert len(system_metrics.network_io) == 2
        
        # Collect service metrics
        service_metrics = collector.collect_service_metrics('test_service')
        
        assert service_metrics.service_name == 'test_service'
        assert service_metrics.requests_per_second >= 0
        assert service_metrics.uptime_seconds >= 0
    
    def test_alert_generation_and_routing(self):
        """Test alert generation from health checks."""
        from services.monitoring.health_service import (
            AlertManager, 
            HealthCheck, 
            HealthStatus, 
            ServiceType
        )
        
        alert_manager = AlertManager()
        
        # Add test alert rules
        alert_manager.add_alert_rule({
            'name': 'service_critical',
            'status': 'critical',
            'severity': 'critical',
            'message_template': 'CRITICAL: {service} is down - {message}'
        })
        
        alert_manager.add_alert_rule({
            'name': 'high_response_time',
            'response_time_threshold_ms': 5000,
            'severity': 'warning',
            'message_template': 'WARNING: {service} slow response ({response_time:.0f}ms)'
        })
        
        # Test critical service alert
        critical_health = HealthCheck(
            service_name='critical_service',
            service_type=ServiceType.API,
            status=HealthStatus.CRITICAL,
            response_time_ms=0,
            message='Connection timeout',
            metadata={'error': 'timeout'},
            timestamp=datetime.now()
        )
        
        alerts = alert_manager.evaluate_health_check(critical_health)
        
        assert len(alerts) >= 1
        critical_alert = next(a for a in alerts if a['rule_name'] == 'service_critical')
        assert critical_alert['severity'] == 'critical'
        assert 'critical_service' in critical_alert['message']
        
        # Test slow response alert
        slow_health = HealthCheck(
            service_name='slow_service',
            service_type=ServiceType.API,
            status=HealthStatus.HEALTHY,
            response_time_ms=6000,  # 6 seconds
            message='Slow response',
            metadata={},
            timestamp=datetime.now()
        )
        
        alerts = alert_manager.evaluate_health_check(slow_health)
        
        slow_alert = next((a for a in alerts if a['rule_name'] == 'high_response_time'), None)
        assert slow_alert is not None
        assert slow_alert['severity'] == 'warning'


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short", 
        "-x",  # Stop on first failure
        "--disable-warnings"
    ])
