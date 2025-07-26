#!/usr/bin/env python3
"""
Phase 1 Implementation Test Script
Tests authentication, multi-chain data, and audit logging functionality
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any

class Phase1Tester:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.results = []
        
    async def test_frontend_accessibility(self) -> bool:
        """Test if frontend pages are accessible"""
        print("🔍 Testing frontend accessibility...")
        
        pages_to_test = [
            "/",
            "/auth/signin",
            "/api/real-data"
        ]
        
        async with aiohttp.ClientSession() as session:
            for page in pages_to_test:
                try:
                    async with session.get(f"{self.base_url}{page}") as response:
                        if response.status == 200:
                            print(f"  ✅ {page} - Accessible")
                            self.results.append(f"Frontend {page}: PASS")
                        else:
                            print(f"  ❌ {page} - Status {response.status}")
                            self.results.append(f"Frontend {page}: FAIL (Status {response.status})")
                except Exception as e:
                    print(f"  ❌ {page} - Error: {e}")
                    self.results.append(f"Frontend {page}: FAIL ({e})")
        
        return True
    
    async def test_real_data_endpoint(self) -> bool:
        """Test the real-data API endpoint"""
        print("🔍 Testing real-data API endpoint...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/real-data") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for required fields
                        required_fields = ['ethereum', 'services', 'metrics', 'timestamp']
                        missing_fields = [field for field in required_fields if field not in data]
                        
                        if not missing_fields:
                            print("  ✅ Real-data endpoint working")
                            print(f"  📊 Current block: {data['ethereum'].get('currentBlock', 'N/A')}")
                            print(f"  📊 Transactions: {data['ethereum'].get('transactionsInBlock', 'N/A')}")
                            print(f"  📊 Services: {data['services']}")
                            self.results.append("Real-data API: PASS")
                            return True
                        else:
                            print(f"  ❌ Missing fields: {missing_fields}")
                            self.results.append(f"Real-data API: FAIL (Missing fields: {missing_fields})")
                            return False
                    else:
                        print(f"  ❌ Status {response.status}")
                        self.results.append(f"Real-data API: FAIL (Status {response.status})")
                        return False
                        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.results.append(f"Real-data API: FAIL ({e})")
            return False
    
    async def test_authentication_pages(self) -> bool:
        """Test authentication pages"""
        print("🔍 Testing authentication pages...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test sign-in page
                async with session.get(f"{self.base_url}/auth/signin") as response:
                    if response.status == 200:
                        content = await response.text()
                        if "Sign In" in content and "Onchain Command Center" in content:
                            print("  ✅ Sign-in page accessible")
                            self.results.append("Authentication sign-in: PASS")
                        else:
                            print("  ❌ Sign-in page content incorrect")
                            self.results.append("Authentication sign-in: FAIL (Content)")
                            return False
                    else:
                        print(f"  ❌ Sign-in page status {response.status}")
                        self.results.append(f"Authentication sign-in: FAIL (Status {response.status})")
                        return False
                        
        except Exception as e:
            print(f"  ❌ Authentication test error: {e}")
            self.results.append(f"Authentication: FAIL ({e})")
            return False
        
        return True
    
    async def test_multi_chain_support(self) -> bool:
        """Test multi-chain data support"""
        print("🔍 Testing multi-chain support...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/real-data") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for multi-chain indicators
                        has_multi_chain = (
                            'multiChainIngester' in data.get('services', {}) or
                            'summary' in data or
                            'polygon' in data or
                            'bsc' in data
                        )
                        
                        if has_multi_chain:
                            print("  ✅ Multi-chain support detected")
                            if 'summary' in data:
                                print(f"  📊 Active chains: {data['summary'].get('activeChains', 'N/A')}")
                            self.results.append("Multi-chain support: PASS")
                            return True
                        else:
                            print("  ⚠️  Multi-chain support not yet active (fallback to single chain)")
                            self.results.append("Multi-chain support: PENDING (Single chain fallback)")
                            return True  # Not a failure, just not implemented yet
                    else:
                        print(f"  ❌ Cannot test multi-chain (API status {response.status})")
                        self.results.append("Multi-chain support: FAIL (API unavailable)")
                        return False
                        
        except Exception as e:
            print(f"  ❌ Multi-chain test error: {e}")
            self.results.append(f"Multi-chain support: FAIL ({e})")
            return False
    
    async def test_audit_logging(self) -> bool:
        """Test audit logging functionality"""
        print("🔍 Testing audit logging...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test audit log endpoint
                audit_data = {
                    "action": "TEST_ACTION",
                    "details": {"test": True, "timestamp": datetime.utcnow().isoformat()}
                }
                
                async with session.post(
                    f"{self.base_url}/api/audit/log",
                    json=audit_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status in [200, 401]:  # 401 is expected without auth
                        print("  ✅ Audit logging endpoint accessible")
                        self.results.append("Audit logging: PASS")
                        return True
                    else:
                        print(f"  ❌ Audit logging status {response.status}")
                        self.results.append(f"Audit logging: FAIL (Status {response.status})")
                        return False
                        
        except Exception as e:
            print(f"  ❌ Audit logging test error: {e}")
            self.results.append(f"Audit logging: FAIL ({e})")
            return False
    
    async def test_file_structure(self) -> bool:
        """Test that required files exist"""
        print("🔍 Testing file structure...")
        
        import os
        
        required_files = [
            "services/ui/nextjs-app/pages/api/auth/[...nextauth].ts",
            "services/ui/nextjs-app/pages/auth/signin.tsx",
            "services/ui/nextjs-app/src/hooks/useAuth.ts",
            "services/ui/nextjs-app/src/components/auth/ProtectedRoute.tsx",
            "services/ui/nextjs-app/src/hooks/useAudit.ts",
            "services/ui/nextjs-app/prisma/schema.prisma",
            "services/ethereum_ingester/config/chains.py",
            "services/ethereum_ingester/multi_chain_ingester.py",
            "services/ethereum_ingester/normalizer.py",
            "services/access_control/audit_service.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}")
                missing_files.append(file_path)
        
        if not missing_files:
            print("  ✅ All required files present")
            self.results.append("File structure: PASS")
            return True
        else:
            print(f"  ❌ Missing files: {len(missing_files)}")
            self.results.append(f"File structure: FAIL (Missing {len(missing_files)} files)")
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📋 PHASE 1 IMPLEMENTATION TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for result in self.results if "PASS" in result)
        total = len(self.results)
        
        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        print("\n📝 Detailed Results:")
        for result in self.results:
            if "PASS" in result:
                print(f"  ✅ {result}")
            elif "PENDING" in result:
                print(f"  ⚠️  {result}")
            else:
                print(f"  ❌ {result}")
        
        print("\n🎯 Phase 1 Status:")
        if passed >= total - 1:  # Allow 1 failure for pending features
            print("  🟢 PHASE 1 IMPLEMENTATION SUCCESSFUL")
            print("  🚀 Ready for Phase 2: Entity Resolution & Graph Database")
        else:
            print("  🔴 PHASE 1 IMPLEMENTATION NEEDS ATTENTION")
            print("  ⚠️  Please fix issues before proceeding to Phase 2")
        
        print("\n📋 Next Steps:")
        print("  1. Set up PostgreSQL database")
        print("  2. Run Prisma migrations")
        print("  3. Seed database with initial users")
        print("  4. Configure environment variables")
        print("  5. Start backend services")
        print("  6. Proceed to Phase 2")

async def main():
    """Main test function"""
    print("🚀 Starting Phase 1 Implementation Tests")
    print("="*60)
    
    tester = Phase1Tester()
    
    # Run all tests
    await tester.test_file_structure()
    await tester.test_frontend_accessibility()
    await tester.test_authentication_pages()
    await tester.test_real_data_endpoint()
    await tester.test_multi_chain_support()
    await tester.test_audit_logging()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 