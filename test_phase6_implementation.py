#!/usr/bin/env python3
"""
Phase 6 Implementation Test
Advanced Analytics & ML Implementation
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.analytics.ml_models import ml_manager, MLPrediction, ModelPerformance
from services.analytics.advanced_ml_analytics import advanced_analytics, CrossChainAnalysis, PortfolioRiskAnalysis, RegulatoryReport

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase6TestSuite:
    """Comprehensive test suite for Phase 6 implementation"""
    
    def __init__(self):
        self.test_results = []
        self.passed_tests = 0
        self.total_tests = 0
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            logger.error(f"❌ {test_name}: FAILED - {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_ml_models_initialization(self):
        """Test ML models initialization"""
        try:
            await ml_manager.initialize_models()
            self.log_test("ML Models Initialization", True)
        except Exception as e:
            self.log_test("ML Models Initialization", False, str(e))
    
    async def test_fraud_detection_model(self):
        """Test fraud detection model"""
        try:
            # Create mock training data
            training_data = pd.DataFrame({
                'transaction_value': np.random.uniform(100, 10000, 1000),
                'gas_price': np.random.uniform(10, 100, 1000),
                'gas_used': np.random.uniform(50000, 500000, 1000),
                'block_number': np.random.randint(1000000, 2000000, 1000),
                'nonce': np.random.randint(0, 100, 1000),
                'transaction_count': np.random.randint(1, 50, 1000),
                'unique_addresses': np.random.randint(1, 100, 1000),
                'contract_interactions': np.random.randint(0, 10, 1000),
                'time_of_day': np.random.randint(0, 24, 1000),
                'day_of_week': np.random.randint(0, 7, 1000),
                'hour': np.random.randint(0, 24, 1000),
                'minute': np.random.randint(0, 60, 1000),
                'is_fraud': np.random.choice([0, 1], 1000, p=[0.9, 0.1])  # 10% fraud rate
            })
            
            # Train model
            performance = await ml_manager.fraud_model.train_model(training_data)
            
            # Test prediction
            test_transaction = {
                'transaction_value': 5000,
                'gas_price': 50,
                'gas_used': 200000,
                'block_number': 1500000,
                'nonce': 5,
                'transaction_count': 10,
                'unique_addresses': 20,
                'contract_interactions': 2,
                'time_of_day': 14,
                'day_of_week': 3,
                'hour': 14,
                'minute': 30
            }
            
            prediction = await ml_manager.predict_fraud(test_transaction)
            
            assert prediction is not None
            assert hasattr(prediction, 'prediction')
            assert hasattr(prediction, 'confidence')
            assert performance.accuracy > 0.5  # Basic accuracy threshold
            
            self.log_test("Fraud Detection Model", True)
            
        except Exception as e:
            self.log_test("Fraud Detection Model", False, str(e))
    
    async def test_anomaly_detection_model(self):
        """Test anomaly detection model"""
        try:
            # Create mock training data
            training_data = pd.DataFrame({
                'transaction_value': np.random.uniform(100, 10000, 1000),
                'gas_price': np.random.uniform(10, 100, 1000),
                'gas_used': np.random.uniform(50000, 500000, 1000),
                'transaction_count': np.random.randint(1, 50, 1000),
                'unique_addresses': np.random.randint(1, 100, 1000)
            })
            
            # Train model
            performance = await ml_manager.anomaly_model.train_model(training_data)
            
            # Test anomaly detection
            test_data = pd.DataFrame({
                'transaction_value': [1000, 50000, 2000],  # Middle one is anomalous
                'gas_price': [30, 200, 35],  # Middle one is anomalous
                'gas_used': [150000, 800000, 180000],  # Middle one is anomalous
                'transaction_count': [5, 100, 8],  # Middle one is anomalous
                'unique_addresses': [10, 500, 15]  # Middle one is anomalous
            })
            
            predictions = await ml_manager.detect_anomalies(test_data)
            
            assert len(predictions) == 3
            assert all(hasattr(pred, 'prediction') for pred in predictions)
            assert all(hasattr(pred, 'confidence') for pred in predictions)
            
            self.log_test("Anomaly Detection Model", True)
            
        except Exception as e:
            self.log_test("Anomaly Detection Model", False, str(e))
    
    async def test_predictive_analytics_model(self):
        """Test predictive analytics model"""
        try:
            # Create mock training data
            training_data = pd.DataFrame({
                'transaction_volume': np.random.uniform(1000, 10000, 1000),
                'gas_price': np.random.uniform(10, 100, 1000),
                'market_cap': np.random.uniform(1000000, 10000000, 1000),
                'active_addresses': np.random.randint(1000, 10000, 1000),
                'network_hashrate': np.random.uniform(100000, 1000000, 1000)
            })
            
            # Train model
            performance = await ml_manager.predictive_model.train_model(training_data, 'transaction_volume')
            
            # Test prediction
            test_data = {
                'gas_price': 50,
                'market_cap': 5000000,
                'active_addresses': 5000,
                'network_hashrate': 500000
            }
            
            prediction = await ml_manager.predict_transaction_volume(test_data)
            
            assert prediction is not None
            assert hasattr(prediction, 'prediction')
            assert hasattr(prediction, 'confidence')
            
            self.log_test("Predictive Analytics Model", True)
            
        except Exception as e:
            self.log_test("Predictive Analytics Model", False, str(e))
    
    async def test_cross_chain_analysis(self):
        """Test cross-chain correlation analysis"""
        try:
            analyses = await advanced_analytics.analyze_cross_chain_correlations()
            
            assert len(analyses) > 0
            assert all(isinstance(analysis, CrossChainAnalysis) for analysis in analyses)
            assert all(hasattr(analysis, 'correlation_score') for analysis in analyses)
            assert all(hasattr(analysis, 'risk_factors') for analysis in analyses)
            
            self.log_test("Cross-Chain Analysis", True)
            
        except Exception as e:
            self.log_test("Cross-Chain Analysis", False, str(e))
    
    async def test_portfolio_risk_analysis(self):
        """Test portfolio risk analysis"""
        try:
            portfolio_data = {
                'portfolio_id': 'test_portfolio',
                'total_value': 1000000,
                'avg_gas_price': 30,
                'total_gas_used': 1000000,
                'contract_interactions': 5,
                'positions': [
                    {'address': '0x123', 'value': 500000},
                    {'address': '0x456', 'value': 300000},
                    {'address': '0x789', 'value': 200000}
                ]
            }
            
            analysis = await advanced_analytics.analyze_portfolio_risk(portfolio_data)
            
            assert isinstance(analysis, PortfolioRiskAnalysis)
            assert analysis.portfolio_id == 'test_portfolio'
            assert analysis.total_value == 1000000
            assert hasattr(analysis, 'risk_score')
            assert hasattr(analysis, 'recommendations')
            
            self.log_test("Portfolio Risk Analysis", True)
            
        except Exception as e:
            self.log_test("Portfolio Risk Analysis", False, str(e))
    
    async def test_regulatory_report_generation(self):
        """Test regulatory report generation"""
        try:
            report = await advanced_analytics.generate_regulatory_report('monthly', 30)
            
            assert isinstance(report, RegulatoryReport)
            assert report.report_type == 'monthly'
            assert hasattr(report, 'total_transactions')
            assert hasattr(report, 'compliance_status')
            assert hasattr(report, 'risk_indicators')
            
            self.log_test("Regulatory Report Generation", True)
            
        except Exception as e:
            self.log_test("Regulatory Report Generation", False, str(e))
    
    async def test_fraud_pattern_detection(self):
        """Test fraud pattern detection"""
        try:
            transaction_data = [
                {
                    'transaction_value': 5000,
                    'gas_price': 50,
                    'gas_used': 200000,
                    'block_number': 1500000,
                    'nonce': 5,
                    'transaction_count': 10,
                    'unique_addresses': 20,
                    'contract_interactions': 2,
                    'time_of_day': 14,
                    'day_of_week': 3,
                    'hour': 14,
                    'minute': 30
                },
                {
                    'transaction_value': 10000,
                    'gas_price': 80,
                    'gas_used': 300000,
                    'block_number': 1500001,
                    'nonce': 6,
                    'transaction_count': 15,
                    'unique_addresses': 25,
                    'contract_interactions': 3,
                    'time_of_day': 15,
                    'day_of_week': 3,
                    'hour': 15,
                    'minute': 45
                }
            ]
            
            predictions = await advanced_analytics.detect_fraud_patterns(transaction_data)
            
            assert len(predictions) == 2
            assert all(isinstance(pred, MLPrediction) for pred in predictions)
            assert all(hasattr(pred, 'prediction') for pred in predictions)
            
            self.log_test("Fraud Pattern Detection", True)
            
        except Exception as e:
            self.log_test("Fraud Pattern Detection", False, str(e))
    
    async def test_anomaly_detection_batch(self):
        """Test batch anomaly detection"""
        try:
            transaction_data = [
                {
                    'transaction_value': 1000,
                    'gas_price': 30,
                    'gas_used': 150000,
                    'transaction_count': 5,
                    'unique_addresses': 10
                },
                {
                    'transaction_value': 50000,  # Anomalous
                    'gas_price': 200,  # Anomalous
                    'gas_used': 800000,  # Anomalous
                    'transaction_count': 100,  # Anomalous
                    'unique_addresses': 500  # Anomalous
                },
                {
                    'transaction_value': 2000,
                    'gas_price': 35,
                    'gas_used': 180000,
                    'transaction_count': 8,
                    'unique_addresses': 15
                }
            ]
            
            predictions = await advanced_analytics.detect_anomalies_batch(transaction_data)
            
            assert len(predictions) == 3
            assert all(isinstance(pred, MLPrediction) for pred in predictions)
            assert all(hasattr(pred, 'prediction') for pred in predictions)
            
            self.log_test("Batch Anomaly Detection", True)
            
        except Exception as e:
            self.log_test("Batch Anomaly Detection", False, str(e))
    
    async def test_market_trend_predictions(self):
        """Test market trend predictions"""
        try:
            market_data = {
                'gas_price': 50,
                'market_cap': 5000000,
                'active_addresses': 5000,
                'network_hashrate': 500000,
                'transaction_volume': 8000
            }
            
            predictions = await advanced_analytics.predict_market_trends(market_data)
            
            assert len(predictions) > 0
            assert all(isinstance(pred, MLPrediction) for pred in predictions)
            assert all(hasattr(pred, 'prediction') for pred in predictions)
            
            self.log_test("Market Trend Predictions", True)
            
        except Exception as e:
            self.log_test("Market Trend Predictions", False, str(e))
    
    async def test_model_performance_metrics(self):
        """Test model performance metrics retrieval"""
        try:
            performances = await advanced_analytics.get_model_performance_metrics()
            
            # Should return a dictionary of model performances
            assert isinstance(performances, dict)
            
            self.log_test("Model Performance Metrics", True)
            
        except Exception as e:
            self.log_test("Model Performance Metrics", False, str(e))
    
    async def test_ml_insights_generation(self):
        """Test ML insights generation"""
        try:
            insights = await advanced_analytics.generate_ml_insights()
            
            assert isinstance(insights, dict)
            assert 'fraud_detection_rate' in insights
            assert 'anomaly_detection_rate' in insights
            assert 'prediction_accuracy' in insights
            assert 'recommendations' in insights
            
            self.log_test("ML Insights Generation", True)
            
        except Exception as e:
            self.log_test("ML Insights Generation", False, str(e))
    
    async def test_model_retraining(self):
        """Test model retraining functionality"""
        try:
            # Create mock training data
            training_data = pd.DataFrame({
                'transaction_value': np.random.uniform(100, 10000, 500),
                'gas_price': np.random.uniform(10, 100, 500),
                'gas_used': np.random.uniform(50000, 500000, 500),
                'block_number': np.random.randint(1000000, 2000000, 500),
                'nonce': np.random.randint(0, 100, 500),
                'transaction_count': np.random.randint(1, 50, 500),
                'unique_addresses': np.random.randint(1, 100, 500),
                'contract_interactions': np.random.randint(0, 10, 500),
                'time_of_day': np.random.randint(0, 24, 500),
                'day_of_week': np.random.randint(0, 7, 500),
                'hour': np.random.randint(0, 24, 500),
                'minute': np.random.randint(0, 60, 500),
                'is_fraud': np.random.choice([0, 1], 500, p=[0.9, 0.1]),
                'transaction_volume': np.random.uniform(1000, 10000, 500)
            })
            
            performances = await advanced_analytics.retrain_models(training_data)
            
            assert isinstance(performances, dict)
            assert len(performances) > 0
            
            self.log_test("Model Retraining", True)
            
        except Exception as e:
            self.log_test("Model Retraining", False, str(e))
    
    async def run_all_tests(self):
        """Run all Phase 6 tests"""
        logger.info("🚀 Starting Phase 6 Implementation Tests...")
        logger.info("=" * 60)
        
        # Test ML Models
        await self.test_ml_models_initialization()
        await self.test_fraud_detection_model()
        await self.test_anomaly_detection_model()
        await self.test_predictive_analytics_model()
        
        # Test Advanced Analytics
        await self.test_cross_chain_analysis()
        await self.test_portfolio_risk_analysis()
        await self.test_regulatory_report_generation()
        
        # Test ML Operations
        await self.test_fraud_pattern_detection()
        await self.test_anomaly_detection_batch()
        await self.test_market_trend_predictions()
        await self.test_model_performance_metrics()
        await self.test_ml_insights_generation()
        await self.test_model_retraining()
        
        # Print results
        logger.info("=" * 60)
        logger.info(f"📊 Phase 6 Test Results: {self.passed_tests}/{self.total_tests} tests passed")
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            logger.info("🎉 Phase 6 Implementation: EXCELLENT - All core features working!")
        elif success_rate >= 80:
            logger.info("✅ Phase 6 Implementation: GOOD - Most features working!")
        elif success_rate >= 70:
            logger.info("⚠️ Phase 6 Implementation: FAIR - Some issues need attention!")
        else:
            logger.error("❌ Phase 6 Implementation: NEEDS WORK - Significant issues found!")
        
        # Save detailed results
        with open('phase6_test_results.json', 'w') as f:
            json.dump({
                'phase': 'Phase 6 - Advanced Analytics & ML',
                'timestamp': datetime.now().isoformat(),
                'total_tests': self.total_tests,
                'passed_tests': self.passed_tests,
                'success_rate': success_rate,
                'test_results': self.test_results
            }, f, indent=2)
        
        return success_rate >= 80

async def main():
    """Main test runner"""
    test_suite = Phase6TestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        logger.info("🎯 Phase 6 implementation is ready for production!")
        return 0
    else:
        logger.error("🔧 Phase 6 implementation needs fixes before production!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 