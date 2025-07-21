"""
Unit tests for individual service components.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta


class TestEthereumIngester:
    """Unit tests for Ethereum ingestion service."""
    
    def test_event_normalization(self):
        """Test transaction event normalization."""
        from services.ethereum_ingester.ethereum_ingester import EventNormalizer
        
        normalizer = EventNormalizer()
        
        raw_transaction = {
            'hash': '0x123abc',
            'from': '0xsender',
            'to': '0xrecipient', 
            'value': 1000000000000000000,  # 1 ETH in wei
            'gasPrice': 20000000000,  # 20 gwei
            'gas': 21000,
            'gasUsed': 21000
        }
        
        normalized = normalizer.normalize_transaction(raw_transaction, 18500000)
        
        assert normalized['event_name'] == 'TRANSACTION'
        assert normalized['chain_id'] == 1
        assert normalized['block_number'] == 18500000
        assert normalized['from_address'] == '0xsender'
        assert normalized['to_address'] == '0xrecipient'
        assert normalized['value_eth'] == 1.0
        assert normalized['gas_price_gwei'] == 20.0
    
    def test_value_usd_calculation(self):
        """Test USD value calculation."""
        from services.ethereum_ingester.ethereum_ingester import ValueCalculator
        
        calculator = ValueCalculator()
        
        # Mock ETH price
        with patch.object(calculator, 'get_eth_price_usd', return_value=2000.0):
            usd_value = calculator.calculate_usd_value(1.5)  # 1.5 ETH
            assert usd_value == 3000.0
    
    @pytest.mark.asyncio
    async def test_block_processing(self):
        """Test block processing logic."""
        with patch('services.ethereum_ingester.ethereum_ingester.Web3') as mock_web3:
            from services.ethereum_ingester.ethereum_ingester import EthereumIngester
            
            # Mock Web3 instance
            mock_instance = Mock()
            mock_instance.eth.get_block.return_value = Mock(
                number=18500000,
                timestamp=1640995200,
                transactions=[Mock(hash='0x123', **{'from': '0xabc'})]
            )
            mock_web3.return_value = mock_instance
            
            ingester = EthereumIngester()
            
            # Mock the publishing method
            published_events = []
            async def mock_publish(event):
                published_events.append(event)
            ingester._publish_event = mock_publish
            
            await ingester._process_block(18500000)
            
            assert len(published_events) > 0
            assert published_events[0]['block_number'] == 18500000


class TestMEVAgent:
    """Unit tests for MEV detection agent."""
    
    def test_gas_price_anomaly_detection(self):
        """Test gas price anomaly detection."""
        from services.mev_agent.mev_agent import GasPriceAnalyzer
        
        analyzer = GasPriceAnalyzer()
        
        # Normal gas prices
        normal_prices = [20, 22, 25, 21, 24, 23, 26]
        assert not analyzer.is_anomalous_gas_price(25, normal_prices)
        
        # Anomalous gas price
        assert analyzer.is_anomalous_gas_price(200, normal_prices)
    
    def test_sandwich_attack_pattern(self):
        """Test sandwich attack pattern recognition."""
        from services.mev_agent.mev_agent import SandwichDetector
        
        detector = SandwichDetector()
        
        # Simulate sandwich attack transactions
        transactions = [
            {'hash': '0x1', 'from': '0xbot', 'gasPrice': 100, 'to': '0xuniswap'},
            {'hash': '0x2', 'from': '0xvictim', 'gasPrice': 50, 'to': '0xuniswap'}, 
            {'hash': '0x3', 'from': '0xbot', 'gasPrice': 30, 'to': '0xuniswap'}
        ]
        
        is_sandwich = detector.detect_sandwich_pattern(transactions)
        assert is_sandwich == True
    
    def test_mev_signal_generation(self):
        """Test MEV signal data structure."""
        from services.mev_agent.mev_agent import MEVSignal
        
        signal = MEVSignal(
            signal_id="MEV_001",
            agent_name="mev_watch",
            signal_type="SANDWICH_ATTACK",
            confidence_score=0.95,
            related_addresses=["0xbot", "0xvictim"],
            related_transactions=["0x123", "0x456"],
            description="Sandwich attack detected on Uniswap",
            severity="HIGH"
        )
        
        assert signal.signal_id == "MEV_001"
        assert signal.signal_type == "SANDWICH_ATTACK"
        assert signal.confidence_score == 0.95
        assert len(signal.related_addresses) == 2


class TestEntityResolution:
    """Unit tests for entity resolution service."""
    
    def test_address_clustering_features(self):
        """Test address clustering feature extraction."""
        from services.entity_resolution.pipeline import FeatureExtractor
        
        extractor = FeatureExtractor()
        
        address_data = {
            'address': '0xabc123',
            'transaction_count': 1500,
            'total_volume_eth': 250.5,
            'unique_counterparts': 45,
            'first_seen': '2023-01-01',
            'last_seen': '2023-12-01'
        }
        
        features = extractor.extract_features(address_data)
        
        assert 'tx_frequency' in features
        assert 'avg_tx_value' in features  
        assert 'network_centrality' in features
        assert 'activity_duration_days' in features
    
    def test_entity_confidence_scoring(self):
        """Test entity resolution confidence scoring."""
        from services.entity_resolution.pipeline import ConfidenceScorer
        
        scorer = ConfidenceScorer()
        
        # High confidence match
        match_data = {
            'feature_similarity': 0.95,
            'transaction_overlap': 0.8,
            'temporal_correlation': 0.9,
            'gas_pattern_similarity': 0.85
        }
        
        confidence = scorer.calculate_confidence(match_data)
        assert confidence > 0.8
        
        # Low confidence match
        match_data['feature_similarity'] = 0.3
        match_data['transaction_overlap'] = 0.1
        
        confidence = scorer.calculate_confidence(match_data)
        assert confidence < 0.5
    
    @pytest.mark.asyncio
    async def test_entity_graph_update(self):
        """Test entity graph database updates."""
        with patch('neo4j.GraphDatabase.driver') as mock_driver:
            from services.entity_resolution.pipeline import GraphUpdater
            
            updater = GraphUpdater()
            
            entity_data = {
                'entity_id': 'ENT_001',
                'addresses': ['0xabc', '0xdef'],
                'entity_type': 'EXCHANGE',
                'confidence': 0.92
            }
            
            await updater.update_entity_graph(entity_data)
            
            # Verify Neo4j session was used
            mock_driver.return_value.session.return_value.__enter__.return_value.run.assert_called()


class TestGraphAPI:
    """Unit tests for GraphQL API service."""
    
    def test_graphql_schema_validation(self):
        """Test GraphQL schema structure."""
        from services.graph_api.schema import schema
        
        # Check core types exist
        type_map = schema.type_map
        assert 'Entity' in type_map
        assert 'Address' in type_map
        assert 'Transaction' in type_map
        assert 'Query' in type_map
    
    def test_entity_resolver(self):
        """Test entity resolver functionality."""
        from services.graph_api.resolvers import get_entities
        
        # Mock database response
        mock_entities = [
            {
                'id': 'ENT_001',
                'type': 'EXCHANGE',
                'addresses': ['0xabc', '0xdef'],
                'confidence': 0.95
            }
        ]
        
        with patch('services.graph_api.resolvers.query_database', return_value=mock_entities):
            entities = get_entities(None, limit=10)
            
            assert len(entities) == 1
            assert entities[0]['id'] == 'ENT_001'
            assert entities[0]['type'] == 'EXCHANGE'
    
    def test_relationship_resolver(self):
        """Test relationship resolver."""
        from services.graph_api.resolvers import get_relationships
        
        mock_relationships = [
            {
                'from_entity': 'ENT_001',
                'to_entity': 'ENT_002', 
                'relationship_type': 'TRANSACTED_WITH',
                'strength': 0.8
            }
        ]
        
        with patch('services.graph_api.resolvers.query_relationships', return_value=mock_relationships):
            relationships = get_relationships(None, entity_id='ENT_001')
            
            assert len(relationships) == 1
            assert relationships[0]['relationship_type'] == 'TRANSACTED_WITH'


class TestAccessControl:
    """Unit tests for access control service."""
    
    def test_policy_evaluation(self):
        """Test access control policy evaluation."""
        from services.access_control.audit_sink import PolicyEvaluator
        
        evaluator = PolicyEvaluator()
        
        # Load test policy
        policy = {
            'resource': 'onchain_data.curated_events',
            'rules': [
                {
                    'principal': 'analyst@company.com',
                    'action': 'SELECT',
                    'columns': ['transaction_hash', 'block_number', 'from_address'],
                    'conditions': ['value_usd < 10000']
                }
            ]
        }
        
        # Test allowed access
        result = evaluator.evaluate_access(
            user='analyst@company.com',
            resource='onchain_data.curated_events',
            action='SELECT',
            columns=['transaction_hash'],
            context={'value_usd': 5000}
        )
        
        assert result['allowed'] == True
        
        # Test denied access (high value)
        result = evaluator.evaluate_access(
            user='analyst@company.com',
            resource='onchain_data.curated_events', 
            action='SELECT',
            columns=['transaction_hash'],
            context={'value_usd': 50000}
        )
        
        assert result['allowed'] == False
    
    def test_data_masking_rules(self):
        """Test data masking functionality."""
        from services.access_control.audit_sink import DataMasker
        
        masker = DataMasker()
        
        # Test PII masking
        test_data = {
            'email': 'user@test.com',
            'phone': '+1-555-123-4567',
            'wallet_address': '0x742d35Cc6639C0532fE9f484Bd8A0E22E1E7d6C1',
            'transaction_hash': '0x123abc456def'
        }
        
        masked = masker.mask_sensitive_data(test_data, user_role='analyst')
        
        # Blockchain data should remain
        assert masked['wallet_address'] == test_data['wallet_address']
        assert masked['transaction_hash'] == test_data['transaction_hash']
        
        # PII should be masked
        assert masked['email'] != test_data['email']
        assert '***' in masked['phone']


class TestVoiceOps:
    """Unit tests for voice operations service."""
    
    def test_command_parsing(self):
        """Test voice command parsing."""
        from services.voiceops.voice_service import CommandProcessor
        
        processor = CommandProcessor()
        
        # Test show signals command
        command = processor.parse_command("show me recent signals")
        assert command.intent == "show_signals"
        
        # Test address search command
        command = processor.parse_command("search address 0x742d35Cc6639C0532fE9f484Bd8A0E22E1E7d6C1")
        assert command.intent == "search_address"
        assert command.entities['address'] == '0x742d35Cc6639C0532fE9f484Bd8A0E22E1E7d6C1'
        
        # Test alert level command
        command = processor.parse_command("set alert level to high")
        assert command.intent == "alert_level"
        assert command.entities['level'] == 'high'
    
    def test_alert_template_formatting(self):
        """Test alert message template formatting."""
        from services.voiceops.voice_service import AlertTemplates
        
        # Test MEV attack template
        message = AlertTemplates.MEV_ATTACK.format(
            description="Sandwich attack on Uniswap",
            confidence=95
        )
        
        assert "Sandwich attack on Uniswap" in message
        assert "95%" in message
        assert "Critical MEV attack detected" in message
    
    @pytest.mark.asyncio
    async def test_voice_alert_generation(self):
        """Test voice alert generation from signals."""
        from services.voiceops.voice_service import VoiceOpsService
        
        service = VoiceOpsService()
        
        # Test signal to alert conversion
        signal = {
            'signal_type': 'HIGH_VALUE_TRANSFER',
            'description': 'Large whale movement detected',
            'severity': 'HIGH',
            'confidence_score': 0.92,
            'metadata': {'value_usd': 5000000},
            'related_addresses': ['0xwhale123', '0xexchange456']
        }
        
        alert = service.create_signal_alert(signal)
        
        assert alert.priority.value == 'high'
        assert 'whale movement' in alert.message.lower()
        assert '5000000' in alert.message


class TestWorkflowBuilder:
    """Unit tests for workflow builder service."""
    
    def test_workflow_configuration_parsing(self):
        """Test workflow configuration parsing."""
        from services.workflow_builder.sample_signal import build_custom_workflow
        
        config = {
            'name': 'test_high_value_monitor',
            'ops': {
                'fetch_blockchain_data': {
                    'config': {
                        'query': 'SELECT * FROM transactions WHERE value > 1000000',
                        'parameters': {}
                    }
                },
                'detect_anomalies': {
                    'config': {
                        'threshold': 5000000,
                        'comparison': 'greater_than',
                        'metric': 'value_usd'
                    }
                }
            }
        }
        
        workflow = build_custom_workflow(config)
        assert workflow.name == 'test_high_value_monitor'
    
    def test_data_filtering_operation(self):
        """Test data filtering operation."""
        import pandas as pd
        from services.workflow_builder.sample_signal import filter_data
        from unittest.mock import Mock
        
        # Mock context
        context = Mock()
        context.op_config = {
            'conditions': {
                'value_usd': {'operator': 'gt', 'value': 10000},
                'event_type': {'operator': 'eq', 'value': 'TRANSFER'}
            }
        }
        
        # Test data
        test_data = pd.DataFrame([
            {'value_usd': 5000, 'event_type': 'TRANSFER'},
            {'value_usd': 15000, 'event_type': 'TRANSFER'}, 
            {'value_usd': 20000, 'event_type': 'SWAP'},
            {'value_usd': 25000, 'event_type': 'TRANSFER'}
        ])
        
        filtered = filter_data(context, test_data)
        
        # Should only return transfers > $10,000
        assert len(filtered) == 2
        assert all(filtered['value_usd'] > 10000)
        assert all(filtered['event_type'] == 'TRANSFER')
    
    def test_anomaly_detection_operation(self):
        """Test anomaly detection operation."""
        import pandas as pd
        from services.workflow_builder.sample_signal import detect_anomalies
        from unittest.mock import Mock
        
        context = Mock()
        context.op_config = {
            'threshold': 100000,
            'comparison': 'greater_than',
            'metric': 'value_usd'
        }
        
        test_data = pd.DataFrame([
            {'transaction_hash': '0x1', 'value_usd': 50000},
            {'transaction_hash': '0x2', 'value_usd': 150000},  # Anomaly
            {'transaction_hash': '0x3', 'value_usd': 75000},
            {'transaction_hash': '0x4', 'value_usd': 200000}   # Anomaly
        ])
        
        anomalies = detect_anomalies(context, test_data)
        
        assert len(anomalies) == 2
        assert all(anomalies['value_usd'] > 100000)


class TestMonitoringService:
    """Unit tests for monitoring and health service."""
    
    @pytest.mark.asyncio
    async def test_health_check_execution(self):
        """Test health check execution."""
        from services.monitoring.health_service import HealthChecker, HealthStatus
        
        async with HealthChecker() as checker:
            # Mock successful HTTP response
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {'status': 'healthy'}
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = await checker.check_http_service(
                    'test_service',
                    'http://localhost:8001'
                )
                
                assert result.service_name == 'test_service'
                assert result.status == HealthStatus.HEALTHY
                assert result.response_time_ms > 0
    
    def test_metrics_collection(self):
        """Test system metrics collection.""" 
        from services.monitoring.health_service import MetricsCollector
        
        collector = MetricsCollector()
        metrics = collector.collect_system_metrics()
        
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0  
        assert metrics.disk_percent >= 0
        assert len(metrics.network_io) == 2  # bytes_sent, bytes_recv
        assert metrics.active_connections >= 0
    
    def test_alert_rule_evaluation(self):
        """Test alert rule evaluation."""
        from services.monitoring.health_service import AlertManager, HealthCheck, HealthStatus, ServiceType
        
        manager = AlertManager()
        
        # Add test alert rule
        rule = {
            'name': 'service_down',
            'status': 'critical',
            'severity': 'critical',
            'message_template': 'Service {service} is down'
        }
        manager.add_alert_rule(rule)
        
        # Test health check that should trigger alert
        health_check = HealthCheck(
            service_name='test_service',
            service_type=ServiceType.API,
            status=HealthStatus.CRITICAL,
            response_time_ms=0,
            message='Connection failed',
            metadata={},
            timestamp=datetime.now()
        )
        
        alerts = manager.evaluate_health_check(health_check)
        
        assert len(alerts) == 1
        assert alerts[0]['rule_name'] == 'service_down'
        assert alerts[0]['severity'] == 'critical'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
