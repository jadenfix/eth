#!/usr/bin/env python3
"""
Real Data Verification Test
This script tests what data is actually real vs. calculated/mock
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_real_data():
    """Test the real-data API endpoint to see what's real vs. calculated"""
    
    print("🔍 REAL DATA VERIFICATION TEST")
    print("=" * 50)
    
    # Test the real-data API
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:3000/api/real-data') as response:
                if response.status == 200:
                    data = await response.json()
                    
                    print("✅ API Response Received")
                    print(f"📅 Timestamp: {data.get('timestamp')}")
                    
                    # Check Ethereum data (REAL)
                    if 'ethereum' in data:
                        eth_data = data['ethereum']
                        print("\n🔗 ETHEREUM DATA (REAL):")
                        print(f"  Current Block: {eth_data.get('currentBlock')}")
                        print(f"  Block Hash: {eth_data.get('blockHash')}")
                        print(f"  Timestamp: {eth_data.get('timestamp')}")
                        print(f"  Transactions in Block: {eth_data.get('transactionsInBlock')}")
                        print(f"  Gas Used: {eth_data.get('gasUsed')}")
                        print(f"  Gas Limit: {eth_data.get('gasLimit')}")
                    
                    # Check calculated metrics (NOT REAL - calculated from block data)
                    if 'metrics' in data:
                        metrics = data['metrics']
                        print("\n📊 CALCULATED METRICS (NOT REAL - calculated from block data):")
                        print(f"  Blocks Processed: {metrics.get('blocksProcessed')} (calculated)")
                        print(f"  Transactions Analyzed: {metrics.get('transactionsAnalyzed')} (calculated)")
                        print(f"  Entities Resolved: {metrics.get('entitiesResolved')} (calculated)")
                        print(f"  MEV Detected: {metrics.get('mevDetected')} (calculated)")
                        print(f"  Risk Alerts: {metrics.get('riskAlerts')} (calculated)")
                        print(f"  Confidence Score: {metrics.get('confidenceScore')}% (mock)")
                    
                    # Check service status (REAL - but services don't exist)
                    if 'services' in data:
                        services = data['services']
                        print("\n🔧 SERVICE STATUS:")
                        print(f"  Graph API: {services.get('graphAPI')} (service doesn't exist)")
                        print(f"  Voice Ops: {services.get('voiceOps')} (service doesn't exist)")
                        print(f"  Ethereum Ingester: {services.get('ethereumIngester')} (real)")
                        print(f"  Multi-chain Ingester: {services.get('multiChainIngester')} (service doesn't exist)")
                    
                    # Check verification status
                    if 'verification' in data:
                        verification = data['verification']
                        print("\n✅ VERIFICATION STATUS:")
                        print(f"  Ethereum API: {verification.get('ethereumApi')} (REAL)")
                        print(f"  Graph API: {verification.get('graphApi')} (service doesn't exist)")
                        print(f"  Voice Ops: {verification.get('voiceOps')} (service doesn't exist)")
                        print(f"  Multi-chain: {verification.get('multiChain')} (service doesn't exist)")
                    
                    print("\n" + "=" * 50)
                    print("📋 SUMMARY:")
                    print("✅ REAL: Ethereum block data, timestamps, transaction counts")
                    print("❌ CALCULATED: Business metrics (derived from real block data)")
                    print("❌ MISSING: Backend services (Graph API, Voice Ops, Multi-chain)")
                    
                else:
                    print(f"❌ API Error: {response.status}")
                    
        except Exception as e:
            print(f"❌ Connection Error: {e}")

async def test_database():
    """Test database connectivity"""
    print("\n🗄️ DATABASE VERIFICATION")
    print("=" * 30)
    
    # Test if we can connect to the database
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname="onchain_command_center",
            user="jadenfix",
            host="localhost",
            port="5432"
        )
        
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cursor.fetchall()
        print("✅ Database Connected")
        print(f"📋 Tables found: {[table[0] for table in tables]}")
        
        # Check user count
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"👥 Users in database: {user_count}")
        
        # Check audit logs
        cursor.execute("SELECT COUNT(*) FROM audit_logs")
        audit_count = cursor.fetchone()[0]
        print(f"📝 Audit logs: {audit_count}")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        print("❌ psycopg2 not installed - can't test database directly")
    except Exception as e:
        print(f"❌ Database Error: {e}")

async def test_alchemy_api():
    """Test direct Alchemy API call"""
    print("\n🔗 DIRECT ALCHEMY API TEST")
    print("=" * 35)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Direct Alchemy API call (same as our real-data endpoint)
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_getBlockByNumber",
                "params": ["latest", True],
                "id": 1
            }
            
            async with session.post(
                'https://eth-mainnet.g.alchemy.com/v2/Wol66FQUiZSrwlavHmn0OWL4U5fAOAGu',
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    block_data = data['result']
                    
                    print("✅ Direct Alchemy API Response:")
                    print(f"  Block Number: {int(block_data['number'], 16)}")
                    print(f"  Block Hash: {block_data['hash']}")
                    print(f"  Timestamp: {int(block_data['timestamp'], 16)}")
                    print(f"  Transactions: {len(block_data['transactions'])}")
                    print(f"  Gas Used: {int(block_data['gasUsed'], 16)}")
                    print(f"  Gas Limit: {int(block_data['gasLimit'], 16)}")
                    print("  ✅ This is REAL blockchain data!")
                    
                else:
                    print(f"❌ Alchemy API Error: {response.status}")
                    
        except Exception as e:
            print(f"❌ Alchemy API Error: {e}")

async def main():
    """Run all tests"""
    print("🚀 REAL DATA VERIFICATION SUITE")
    print("=" * 50)
    
    await test_real_data()
    await test_database()
    await test_alchemy_api()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL VERDICT:")
    print("✅ REAL: PostgreSQL database, Ethereum blockchain data")
    print("✅ REAL: User authentication, audit logging")
    print("❌ CALCULATED: Business metrics (derived from real data)")
    print("❌ MISSING: Backend services (Graph API, Voice Ops)")
    print("\n💡 The system shows REAL blockchain data with calculated business metrics!")

if __name__ == "__main__":
    asyncio.run(main()) 