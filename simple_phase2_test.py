#!/usr/bin/env python3
"""
Simple Phase 2 Test Script
Tests core functionality without complex dependencies
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplePhase2Test:
    def __init__(self):
        self.base_url = "http://localhost:4000"
        self.results = []
        
    async def run_all_tests(self):
        """Run simple Phase 2 tests"""
        logger.info("🚀 Starting Simple Phase 2 Test Suite")
        logger.info("=" * 60)
        
        # Test 1: Check if server is running
        await self.test_server_running()
        
        # Test 2: Test basic endpoints
        await self.test_basic_endpoints()
        
        # Test 3: Test entity resolution
        await self.test_entity_resolution()
        
        # Test 4: Test real data processing
        await self.test_real_data_processing()
        
        # Print results
        self.print_results()
        
    async def test_server_running(self):
        """Test if the Graph API server is running"""
        logger.info("🧪 Testing server connectivity")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Server is running: {data}")
                        self.results.append(("Server Running", "PASS", "Server responded successfully"))
                        return True
                    else:
                        logger.error(f"❌ Server returned status {response.status}")
                        self.results.append(("Server Running", "FAIL", f"Status {response.status}"))
                        return False
        except Exception as e:
            logger.error(f"❌ Server connection failed: {e}")
            self.results.append(("Server Running", "FAIL", str(e)))
            return False
    
    async def test_basic_endpoints(self):
        """Test basic API endpoints"""
        logger.info("🧪 Testing basic endpoints")
        
        endpoints = [
            ("/health", "Health Check"),
            ("/metrics", "Metrics"),
            ("/entity-resolution/sample", "Entity Resolution Sample"),
            ("/graph/analysis/patterns", "Graph Patterns")
        ]
        
        for endpoint, name in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}", timeout=10) as response:
                        if response.status == 200:
                            logger.info(f"✅ {name}: OK")
                            self.results.append((name, "PASS", "Endpoint responded"))
                        else:
                            logger.error(f"❌ {name}: Status {response.status}")
                            self.results.append((name, "FAIL", f"Status {response.status}"))
            except Exception as e:
                logger.error(f"❌ {name}: Error - {e}")
                self.results.append((name, "FAIL", str(e)))
    
    async def test_entity_resolution(self):
        """Test entity resolution functionality"""
        logger.info("🧪 Testing entity resolution")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test sample entity resolution
                async with session.get(f"{self.base_url}/entity-resolution/sample", timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Entity resolution sample: {data.get('clusters_found', 0)} clusters found")
                        self.results.append(("Entity Resolution", "PASS", f"{data.get('clusters_found', 0)} clusters"))
                    else:
                        logger.error(f"❌ Entity resolution failed: Status {response.status}")
                        self.results.append(("Entity Resolution", "FAIL", f"Status {response.status}"))
        except Exception as e:
            logger.error(f"❌ Entity resolution error: {e}")
            self.results.append(("Entity Resolution", "FAIL", str(e)))
    
    async def test_real_data_processing(self):
        """Test real data processing"""
        logger.info("🧪 Testing real data processing")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test real data processing
                async with session.get(f"{self.base_url}/entity-resolution/real-data?limit=10", timeout=20) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ Real data processing: {data.get('transactions_processed', 0)} transactions")
                        self.results.append(("Real Data Processing", "PASS", f"{data.get('transactions_processed', 0)} transactions"))
                    else:
                        logger.error(f"❌ Real data processing failed: Status {response.status}")
                        self.results.append(("Real Data Processing", "FAIL", f"Status {response.status}"))
        except Exception as e:
            logger.error(f"❌ Real data processing error: {e}")
            self.results.append(("Real Data Processing", "FAIL", str(e)))
    
    def print_results(self):
        """Print test results"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 SIMPLE PHASE 2 TEST RESULTS")
        logger.info("=" * 60)
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r[1] == "PASS")
        failed = sum(1 for r in self.results if r[1] == "FAIL")
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"📈 Success Rate: {(passed/total_tests*100):.1f}%")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for name, status, details in self.results:
            status_icon = "✅" if status == "PASS" else "❌"
            logger.info(f"  {status_icon} {name}: {details}")
        
        if passed >= total_tests * 0.8:
            logger.info("\n🎉 PHASE 2 STATUS: PASSED")
            logger.info("✅ Core functionality is working correctly")
        else:
            logger.error("\n💥 PHASE 2 STATUS: FAILED")
            logger.error("❌ Some critical components are not working")
        
        logger.info("=" * 60)

async def main():
    """Main test runner"""
    test_suite = SimplePhase2Test()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 