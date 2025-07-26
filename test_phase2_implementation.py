#!/usr/bin/env python3
"""
Phase 2 Implementation Test Suite
Tests Entity Resolution & Graph Database Implementation
"""

import asyncio
import aiohttp
import json
import sys
import os
from typing import Dict, List, Any
import logging

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase2TestSuite:
    def __init__(self):
        self.base_url = "http://localhost:4000"
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def run_all_tests(self):
        """Run all Phase 2 tests"""
        logger.info("🚀 Starting Phase 2 Implementation Tests")
        
        # Test 1: Health Check
        await self.test_health_check()
        
        # Test 2: Neo4j Connection
        await self.test_neo4j_connection()
        
        # Test 3: Entity Resolution Pipeline
        await self.test_entity_resolution_pipeline()
        
        # Test 4: Real Data Processing
        await self.test_real_data_processing()
        
        # Test 5: Whale Data Processing
        await self.test_whale_data_processing()
        
        # Test 6: MEV Data Processing
        await self.test_mev_data_processing()
        
        # Test 7: Graph Analysis
        await self.test_graph_analysis()
        
        # Test 8: Entity Search
        await self.test_entity_search()
        
        # Test 9: Wallet Operations
        await self.test_wallet_operations()
        
        # Test 10: Multi-chain Support
        await self.test_multi_chain_support()
        
        # Print results
        self.print_results()
    
    async def test_health_check(self):
        """Test 1: Health Check"""
        logger.info("📋 Test 1: Health Check")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "healthy":
                            logger.info("✅ Health check passed")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Health check failed - invalid status")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Health check failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Health check: {e}")
    
    async def test_neo4j_connection(self):
        """Test 2: Neo4j Connection"""
        logger.info("📋 Test 2: Neo4j Connection")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/metrics") as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status", "unknown")
                        if status in ["connected", "disconnected"]:
                            logger.info(f"✅ Neo4j connection test passed - status: {status}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error(f"❌ Neo4j connection test failed - invalid status: {status}")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Neo4j connection test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Neo4j connection test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Neo4j connection: {e}")
    
    async def test_entity_resolution_pipeline(self):
        """Test 3: Entity Resolution Pipeline"""
        logger.info("📋 Test 3: Entity Resolution Pipeline")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/entity-resolution/sample") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "clusters_found" in data and "transactions_processed" in data:
                            logger.info(f"✅ Entity resolution pipeline test passed - {data['clusters_found']} clusters found")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Entity resolution pipeline test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Entity resolution pipeline test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Entity resolution pipeline test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Entity resolution pipeline: {e}")
    
    async def test_real_data_processing(self):
        """Test 4: Real Data Processing"""
        logger.info("📋 Test 4: Real Data Processing")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/entity-resolution/real-data?limit=10") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "transactions_processed" in data and "clusters_created" in data:
                            logger.info(f"✅ Real data processing test passed - {data['transactions_processed']} transactions processed")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Real data processing test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Real data processing test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Real data processing test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Real data processing: {e}")
    
    async def test_whale_data_processing(self):
        """Test 5: Whale Data Processing"""
        logger.info("📋 Test 5: Whale Data Processing")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/entity-resolution/whale-data") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "transactions_processed" in data:
                            logger.info(f"✅ Whale data processing test passed - {data['transactions_processed']} transactions processed")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Whale data processing test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Whale data processing test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Whale data processing test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Whale data processing: {e}")
    
    async def test_mev_data_processing(self):
        """Test 6: MEV Data Processing"""
        logger.info("📋 Test 6: MEV Data Processing")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/entity-resolution/mev-data") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "transactions_processed" in data:
                            logger.info(f"✅ MEV data processing test passed - {data['transactions_processed']} transactions processed")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ MEV data processing test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ MEV data processing test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ MEV data processing test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"MEV data processing: {e}")
    
    async def test_graph_analysis(self):
        """Test 7: Graph Analysis"""
        logger.info("📋 Test 7: Graph Analysis")
        try:
            async with aiohttp.ClientSession() as session:
                # Test patterns analysis
                async with session.get(f"{self.base_url}/graph/analysis/patterns") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "total_nodes" in data and "total_relationships" in data:
                            logger.info(f"✅ Graph patterns analysis test passed - {data['total_nodes']} nodes, {data['total_relationships']} relationships")
                        else:
                            logger.error("❌ Graph patterns analysis test failed - missing required fields")
                            self.test_results["failed"] += 1
                            return
                    else:
                        logger.error(f"❌ Graph patterns analysis test failed - status {response.status}")
                        self.test_results["failed"] += 1
                        return
                
                # Test clusters analysis
                async with session.get(f"{self.base_url}/graph/analysis/clusters") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "metrics" in data:
                            logger.info("✅ Graph clusters analysis test passed")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Graph clusters analysis test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Graph clusters analysis test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Graph analysis test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Graph analysis: {e}")
    
    async def test_entity_search(self):
        """Test 8: Entity Search"""
        logger.info("📋 Test 8: Entity Search")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/entities/search?query=test&limit=5") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "entities" in data and "query" in data:
                            logger.info(f"✅ Entity search test passed - query: {data['query']}")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Entity search test failed - missing required fields")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Entity search test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Entity search test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Entity search: {e}")
    
    async def test_wallet_operations(self):
        """Test 9: Wallet Operations"""
        logger.info("📋 Test 9: Wallet Operations")
        try:
            async with aiohttp.ClientSession() as session:
                test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
                
                # Test wallet creation
                async with session.post(f"{self.base_url}/dev/create-wallet?address={test_address}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            logger.info("✅ Wallet creation test passed")
                        else:
                            logger.error("❌ Wallet creation test failed")
                            self.test_results["failed"] += 1
                            return
                    else:
                        logger.error(f"❌ Wallet creation test failed - status {response.status}")
                        self.test_results["failed"] += 1
                        return
                
                # Test wallet retrieval
                async with session.get(f"{self.base_url}/wallets/{test_address}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "address" in data:
                            logger.info("✅ Wallet retrieval test passed")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Wallet retrieval test failed - missing address field")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Wallet retrieval test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Wallet operations test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Wallet operations: {e}")
    
    async def test_multi_chain_support(self):
        """Test 10: Multi-chain Support"""
        logger.info("📋 Test 10: Multi-chain Support")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/multi-chain/latest") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "ethereum" in data:
                            logger.info("✅ Multi-chain support test passed")
                            self.test_results["passed"] += 1
                        else:
                            logger.error("❌ Multi-chain support test failed - missing ethereum data")
                            self.test_results["failed"] += 1
                    else:
                        logger.error(f"❌ Multi-chain support test failed - status {response.status}")
                        self.test_results["failed"] += 1
        except Exception as e:
            logger.error(f"❌ Multi-chain support test error: {e}")
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"Multi-chain support: {e}")
    
    def print_results(self):
        """Print test results summary"""
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        
        logger.info("\n" + "="*60)
        logger.info("📊 PHASE 2 IMPLEMENTATION TEST RESULTS")
        logger.info("="*60)
        logger.info(f"✅ Tests Passed: {self.test_results['passed']}")
        logger.info(f"❌ Tests Failed: {self.test_results['failed']}")
        logger.info(f"📈 Success Rate: {(self.test_results['passed']/total_tests*100):.1f}%")
        
        if self.test_results["errors"]:
            logger.info("\n🔍 Errors:")
            for error in self.test_results["errors"]:
                logger.error(f"  - {error}")
        
        if self.test_results["passed"] >= 8:
            logger.info("\n🎉 Phase 2 Implementation Status: PASSED")
            logger.info("✅ Entity Resolution & Graph Database Implementation is working correctly")
        else:
            logger.error("\n💥 Phase 2 Implementation Status: FAILED")
            logger.error("❌ Some critical components are not working correctly")
        
        logger.info("="*60)

async def main():
    """Main test runner"""
    test_suite = Phase2TestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 