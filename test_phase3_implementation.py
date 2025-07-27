#!/usr/bin/env python3
"""
Phase 3 Implementation Test Suite
Tests all intelligence agents: MEV detection, whale tracking, risk scoring, and sanctions checking
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase3TestSuite:
    def __init__(self):
        self.base_url = "http://localhost:4000"
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "details": []
        }
    
    async def run_all_tests(self):
        """Run all Phase 3 tests"""
        logger.info("🚀 Starting Phase 3 Implementation Tests...")
        
        tests = [
            ("Phase 3 Status Check", self.test_phase3_status),
            ("MEV Detection", self.test_mev_detection),
            ("MEV Statistics", self.test_mev_statistics),
            ("Whale Tracking", self.test_whale_tracking),
            ("Whale Statistics", self.test_whale_statistics),
            ("Risk Scoring", self.test_risk_scoring),
            ("Feature Importance", self.test_feature_importance),
            ("Sanctions Checking", self.test_sanctions_checking),
            ("Sanctions Statistics", self.test_sanctions_statistics),
            ("End-to-End Integration", self.test_end_to_end_integration)
        ]
        
        for test_name, test_func in tests:
            await self.run_test(test_name, test_func)
        
        self.print_results()
    
    async def run_test(self, test_name: str, test_func):
        """Run a single test"""
        self.results["total"] += 1
        logger.info(f"🧪 Running: {test_name}")
        
        try:
            result = await test_func()
            if result:
                self.results["passed"] += 1
                logger.info(f"✅ PASSED: {test_name}")
                self.results["details"].append({
                    "test": test_name,
                    "status": "PASSED",
                    "details": result
                })
            else:
                self.results["failed"] += 1
                logger.error(f"❌ FAILED: {test_name}")
                self.results["details"].append({
                    "test": test_name,
                    "status": "FAILED",
                    "details": "Test returned False"
                })
        except Exception as e:
            self.results["failed"] += 1
            logger.error(f"❌ FAILED: {test_name} - {str(e)}")
            self.results["details"].append({
                "test": test_name,
                "status": "FAILED",
                "details": str(e)
            })
    
    async def test_phase3_status(self) -> bool:
        """Test Phase 3 status endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/phase3/status") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Phase 3 Status: {data}")
                    return data.get("status") == "operational"
                return False
    
    async def test_mev_detection(self) -> bool:
        """Test MEV detection endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/mev/detect") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"MEV Detection: {data}")
                    return "signals_detected" in data and "signals" in data
                return False
    
    async def test_mev_statistics(self) -> bool:
        """Test MEV statistics endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/mev/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"MEV Statistics: {data}")
                    return "total_signals" in data
                return False
    
    async def test_whale_tracking(self) -> bool:
        """Test whale tracking endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/whale/track") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Whale Tracking: {data}")
                    return "movements_detected" in data and "movements" in data
                return False
    
    async def test_whale_statistics(self) -> bool:
        """Test whale statistics endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/whale/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Whale Statistics: {data}")
                    return "known_whales" in data
                return False
    
    async def test_risk_scoring(self) -> bool:
        """Test risk scoring endpoint"""
        async with aiohttp.ClientSession() as session:
            # Sample address data for risk scoring
            address_data = {
                "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                "address_data": {
                    "transaction_count": 100,
                    "total_volume_eth": 50,
                    "avg_transaction_value": 0.5,
                    "max_transaction_value": 10,
                    "gas_prices": [25, 30, 40, 35, 50],
                    "contract_interactions": 30,
                    "unique_counterparties": 15,
                    "mev_activity_score": 0.2,
                    "whale_movement_score": 0.1,
                    "sanctions_risk_score": 0,
                    "age_days": 180,
                    "balance_history": [5, 8, 3, 12, 6]
                }
            }
            
            async with session.post(
                f"{self.base_url}/risk/calculate",
                json=address_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Risk Scoring: {data}")
                    return "risk_score" in data and "explanation" in data
                return False
    
    async def test_feature_importance(self) -> bool:
        """Test feature importance endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/risk/feature-importance") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Feature Importance: {data}")
                    return "feature_importance" in data
                return False
    
    async def test_sanctions_checking(self) -> bool:
        """Test sanctions checking endpoint"""
        async with aiohttp.ClientSession() as session:
            # Test with known sanctioned address
            request_data = {
                "addresses": [
                    "0x7F367cC41522cE07553e823bf3be79A889DEbe1B",  # Tornado Cash
                    "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"   # Normal address
                ]
            }
            
            async with session.post(
                f"{self.base_url}/sanctions/check",
                json=request_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Sanctions Checking: {data}")
                    return "addresses_checked" in data and "results" in data
                return False
    
    async def test_sanctions_statistics(self) -> bool:
        """Test sanctions statistics endpoint"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/sanctions/statistics") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Sanctions Statistics: {data}")
                    return "total_addresses_checked" in data
                return False
    
    async def test_end_to_end_integration(self) -> bool:
        """Test end-to-end integration of all Phase 3 components"""
        try:
            # Test all services in sequence
            async with aiohttp.ClientSession() as session:
                # 1. Check Phase 3 status
                async with session.get(f"{self.base_url}/phase3/status") as response:
                    if response.status != 200:
                        return False
                
                # 2. Test MEV detection
                async with session.get(f"{self.base_url}/mev/detect") as response:
                    if response.status != 200:
                        return False
                
                # 3. Test whale tracking
                async with session.get(f"{self.base_url}/whale/track") as response:
                    if response.status != 200:
                        return False
                
                # 4. Test risk scoring
                address_data = {
                    "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "address_data": {
                        "transaction_count": 100,
                        "total_volume_eth": 50,
                        "avg_transaction_value": 0.5,
                        "max_transaction_value": 10,
                        "gas_prices": [25, 30, 40, 35, 50],
                        "contract_interactions": 30,
                        "unique_counterparties": 15,
                        "mev_activity_score": 0.2,
                        "whale_movement_score": 0.1,
                        "sanctions_risk_score": 0,
                        "age_days": 180,
                        "balance_history": [5, 8, 3, 12, 6]
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/risk/calculate",
                    json=address_data
                ) as response:
                    if response.status != 200:
                        return False
                
                # 5. Test sanctions checking
                sanctions_data = {
                    "addresses": ["0x7F367cC41522cE07553e823bf3be79A889DEbe1B"]
                }
                
                async with session.post(
                    f"{self.base_url}/sanctions/check",
                    json=sanctions_data
                ) as response:
                    if response.status != 200:
                        return False
                
                logger.info("✅ All Phase 3 services integrated successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ End-to-end integration failed: {e}")
            return False
    
    def print_results(self):
        """Print test results"""
        print("\n" + "="*60)
        print("🎯 PHASE 3 IMPLEMENTATION TEST RESULTS")
        print("="*60)
        
        success_rate = (self.results["passed"] / self.results["total"]) * 100 if self.results["total"] > 0 else 0
        
        print(f"📊 Total Tests: {self.results['total']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)
        
        for detail in self.results["details"]:
            status_icon = "✅" if detail["status"] == "PASSED" else "❌"
            print(f"{status_icon} {detail['test']}")
            if detail["status"] == "FAILED":
                print(f"   Error: {detail['details']}")
        
        print("\n" + "="*60)
        
        if success_rate == 100:
            print("🎉 PHASE 3 IMPLEMENTATION: 100% SUCCESS!")
            print("🚀 All intelligence agents are operational!")
        elif success_rate >= 80:
            print("✅ PHASE 3 IMPLEMENTATION: MOSTLY SUCCESSFUL")
            print("⚠️  Some components need attention")
        else:
            print("❌ PHASE 3 IMPLEMENTATION: NEEDS WORK")
            print("🔧 Several components are failing")
        
        print("="*60)

async def main():
    """Main test runner"""
    test_suite = Phase3TestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 