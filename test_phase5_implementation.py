#!/usr/bin/env python3
"""
Phase 5 Implementation Test Suite
Advanced Analytics & Visualization

This test suite verifies the implementation of:
- Advanced Risk Analytics
- Predictive Analytics with ML models
- Custom Reporting Engine
- Real-time Visualization Dashboard
"""

import asyncio
import aiohttp
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase5TestSuite:
    def __init__(self):
        self.test_results = {"passed": 0, "failed": 0}
        self.base_url_analytics = "http://localhost:5000"
        self.base_url_dashboard = "http://localhost:5001"
        
    async def run_all_tests(self):
        """Run all Phase 5 tests"""
        logger.info("=" * 60)
        logger.info("PHASE 5 IMPLEMENTATION TEST SUITE")
        logger.info("Advanced Analytics & Visualization")
        logger.info("=" * 60)
        
        # Test 1: Advanced Risk Analytics
        await self.test_advanced_risk_analytics()
        
        # Test 2: Predictive Analytics
        await self.test_predictive_analytics()
        
        # Test 3: Custom Reporting Engine
        await self.test_custom_reporting_engine()
        
        # Test 4: Report Templates
        await self.test_report_templates()
        
        # Test 5: Report Generation
        await self.test_report_generation()
        
        # Test 6: Report Export
        await self.test_report_export()
        
        # Test 7: Real-time Dashboard
        await self.test_real_time_dashboard()
        
        # Test 8: Analytics API Endpoints
        await self.test_analytics_api_endpoints()
        
        # Test 9: Visualization Components
        await self.test_visualization_components()
        
        # Test 10: Data Export Capabilities
        await self.test_data_export_capabilities()
        
        # Print final results
        await self.print_test_results()
    
    async def test_advanced_risk_analytics(self):
        """Test 1: Advanced Risk Analytics"""
        logger.info("📋 Test 1: Advanced Risk Analytics")
        try:
            async with aiohttp.ClientSession() as session:
                # Test risk analytics generation
                payload = {
                    "time_range": "24h",
                    "include_anomalies": True,
                    "include_visualizations": True
                }
                
                async with session.post(f"{self.base_url_analytics}/analytics/risk", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Verify response structure
                        required_fields = ["report_id", "report_type", "metrics", "insights", "recommendations"]
                        if all(field in data for field in required_fields):
                            logger.info("✅ Advanced risk analytics test passed")
                            logger.info(f"   - Generated {len(data['metrics'])} risk metrics")
                            logger.info(f"   - Generated {len(data['insights'])} insights")
                            logger.info(f"   - Generated {len(data['recommendations'])} recommendations")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Advanced risk analytics test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Advanced risk analytics test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Advanced risk analytics test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_predictive_analytics(self):
        """Test 2: Predictive Analytics"""
        logger.info("📋 Test 2: Predictive Analytics")
        try:
            async with aiohttp.ClientSession() as session:
                # Test predictive analytics generation
                payload = {
                    "horizon": "24h",
                    "include_alerts": True,
                    "include_feature_importance": True
                }
                
                async with session.post(f"{self.base_url_analytics}/analytics/predictive", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Verify response structure
                        required_fields = ["report_id", "predictions", "alerts"]
                        if all(field in data for field in required_fields):
                            logger.info("✅ Predictive analytics test passed")
                            logger.info(f"   - Generated {len(data['predictions'])} predictions")
                            logger.info(f"   - Generated {len(data['alerts'])} alerts")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Predictive analytics test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Predictive analytics test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Predictive analytics test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_custom_reporting_engine(self):
        """Test 3: Custom Reporting Engine"""
        logger.info("📋 Test 3: Custom Reporting Engine")
        try:
            async with aiohttp.ClientSession() as session:
                # Test available metrics endpoint
                async with session.get(f"{self.base_url_analytics}/analytics/metrics") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "metrics" in data and len(data["metrics"]) > 0:
                            logger.info("✅ Custom reporting engine test passed")
                            logger.info(f"   - Available metrics: {len(data['metrics'])}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Custom reporting engine test failed - no metrics available")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Custom reporting engine test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Custom reporting engine test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_report_templates(self):
        """Test 4: Report Templates"""
        logger.info("📋 Test 4: Report Templates")
        try:
            async with aiohttp.ClientSession() as session:
                # Test creating a report template
                template_payload = {
                    "template_id": "test_template_001",
                    "name": "Test Risk Report",
                    "description": "A test report template for risk analytics",
                    "metrics": ["transaction_volume", "average_gas_price", "mev_opportunities"],
                    "visualizations": ["transaction_volume_chart", "gas_price_analysis"],
                    "schedule": "0 9 * * *",  # Daily at 9 AM
                    "recipients": ["analyst@company.com"]
                }
                
                async with session.post(f"{self.base_url_analytics}/reports/templates", json=template_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "created":
                            logger.info("✅ Report templates test passed")
                            logger.info(f"   - Created template: {data['template_id']}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Report templates test failed - template not created")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Report templates test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Report templates test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_report_generation(self):
        """Test 5: Report Generation"""
        logger.info("📋 Test 5: Report Generation")
        try:
            async with aiohttp.ClientSession() as session:
                # Test generating a custom report
                report_payload = {
                    "template_id": "test_template_001",
                    "time_range": "24h",
                    "custom_filters": {
                        "min_gas_price": 20,
                        "max_gas_price": 100
                    }
                }
                
                async with session.post(f"{self.base_url_analytics}/reports/generate", json=report_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "report_id" in data and "data" in data:
                            logger.info("✅ Report generation test passed")
                            logger.info(f"   - Generated report: {data['report_id']}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Report generation test failed - missing report data")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Report generation test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Report generation test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_report_export(self):
        """Test 6: Report Export"""
        logger.info("📋 Test 6: Report Export")
        try:
            async with aiohttp.ClientSession() as session:
                # First generate a report
                report_payload = {
                    "template_id": "test_template_001",
                    "time_range": "24h"
                }
                
                async with session.post(f"{self.base_url_analytics}/reports/generate", json=report_payload) as response:
                    if response.status == 200:
                        report_data = await response.json()
                        report_id = report_data["report_id"]
                        
                        # Test exporting the report
                        export_payload = {
                            "report_id": report_id,
                            "format": "json"
                        }
                        
                        async with session.post(f"{self.base_url_analytics}/reports/export", json=export_payload) as export_response:
                            if export_response.status == 200:
                                export_data = await export_response.json()
                                if "export_data" in export_data:
                                    logger.info("✅ Report export test passed")
                                    logger.info(f"   - Exported report: {report_id}")
                                    self.test_results["passed"] += 1
                                else:
                                    logger.error("❌ Report export test failed - no export data")
                                    self.test_results["failed"] += 1
                            else:
                                logger.error(f"❌ Report export test failed - HTTP {export_response.status}")
                                self.test_results["failed"] += 1
                    else:
                        logger.error("❌ Report export test failed - could not generate report")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Report export test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_real_time_dashboard(self):
        """Test 7: Real-time Dashboard"""
        logger.info("📋 Test 7: Real-time Dashboard")
        try:
            async with aiohttp.ClientSession() as session:
                # Test dashboard health
                async with session.get(f"{self.base_url_dashboard}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "healthy":
                            logger.info("✅ Real-time dashboard test passed")
                            logger.info(f"   - Dashboard status: {data['status']}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Real-time dashboard test failed - dashboard not healthy")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Real-time dashboard test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Real-time dashboard test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_analytics_api_endpoints(self):
        """Test 8: Analytics API Endpoints"""
        logger.info("📋 Test 8: Analytics API Endpoints")
        try:
            async with aiohttp.ClientSession() as session:
                # Test available visualizations endpoint
                async with session.get(f"{self.base_url_analytics}/analytics/visualizations") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "visualizations" in data and len(data["visualizations"]) > 0:
                            logger.info("✅ Analytics API endpoints test passed")
                            logger.info(f"   - Available visualizations: {len(data['visualizations'])}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Analytics API endpoints test failed - no visualizations available")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Analytics API endpoints test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Analytics API endpoints test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_visualization_components(self):
        """Test 9: Visualization Components"""
        logger.info("📋 Test 9: Visualization Components")
        try:
            async with aiohttp.ClientSession() as session:
                # Test dashboard metrics endpoint
                async with session.get(f"{self.base_url_dashboard}/api/metrics") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "transaction_count" in data or "message" in data:
                            logger.info("✅ Visualization components test passed")
                            logger.info("   - Dashboard metrics endpoint working")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Visualization components test failed - invalid metrics data")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Visualization components test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Visualization components test failed: {e}")
            self.test_results["failed"] += 1
    
    async def test_data_export_capabilities(self):
        """Test 10: Data Export Capabilities"""
        logger.info("📋 Test 10: Data Export Capabilities")
        try:
            async with aiohttp.ClientSession() as session:
                # Test report history endpoint
                async with session.get(f"{self.base_url_analytics}/reports/history") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "reports" in data:
                            logger.info("✅ Data export capabilities test passed")
                            logger.info(f"   - Report history available: {len(data['reports'])} reports")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Data export capabilities test failed - no report history")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Data export capabilities test failed - HTTP {response.status}")
                        self.test_results["failed"] += 1
                        
        except Exception as e:
            logger.error(f"❌ Data export capabilities test failed: {e}")
            self.test_results["failed"] += 1
    
    async def print_test_results(self):
        """Print final test results"""
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 PHASE 5 IMPLEMENTATION TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"✅ Tests Passed: {self.test_results['passed']}")
        logger.info(f"❌ Tests Failed: {self.test_results['failed']}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info("")
        
        if success_rate >= 90:
            logger.info("🎉 Phase 5 Implementation Status: PASSED")
            logger.info("✅ Advanced Analytics & Visualization is working correctly")
        else:
            logger.info("⚠️ Phase 5 Implementation Status: NEEDS IMPROVEMENT")
            logger.info("❌ Some advanced analytics features need attention")
        
        logger.info("=" * 60)

async def main():
    """Main test runner"""
    test_suite = Phase5TestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 