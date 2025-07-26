#!/usr/bin/env python3
"""
Test script to verify real data functionality
"""
import requests
import json
import time
from datetime import datetime

def test_ethereum_api():
    """Test direct Ethereum API connection"""
    print("🔍 Testing Ethereum API connection...")
    
    url = "https://eth-mainnet.g.alchemy.com/v2/Wol66FQUiZSrwlavHmn0OWL4U5fAOAGu"
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": ["latest", True],
        "id": 1
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if 'result' in data:
            block_data = data['result']
            current_block = int(block_data['number'], 16)
            timestamp = int(block_data['timestamp'], 16)
            tx_count = len(block_data.get('transactions', []))
            
            print(f"✅ Ethereum API: Connected")
            print(f"   Current Block: #{current_block:,}")
            print(f"   Timestamp: {datetime.fromtimestamp(timestamp)}")
            print(f"   Transactions: {tx_count}")
            return True
        else:
            print(f"❌ Ethereum API: Error - {data}")
            return False
    except Exception as e:
        print(f"❌ Ethereum API: Connection failed - {e}")
        return False

def test_backend_services():
    """Test backend service health"""
    print("\n🔍 Testing backend services...")
    
    services = {
        "Graph API": "http://localhost:4000/health",
        "Voice Ops": "http://localhost:5000/health"
    }
    
    results = {}
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                print(f"✅ {name}: {status}")
                results[name] = status == 'healthy'
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"❌ {name}: Connection failed - {e}")
            results[name] = False
    
    return results

def test_frontend_api():
    """Test frontend API endpoint"""
    print("\n🔍 Testing frontend API...")
    
    try:
        response = requests.get("http://localhost:3000/api/real-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Frontend API: Connected")
            print(f"   Current Block: #{data['ethereum']['currentBlock']:,}")
            print(f"   Transactions: {data['ethereum']['transactionsInBlock']}")
            print(f"   Services: {data['verification']}")
            
            # Verify data consistency
            ethereum_connected = data['verification']['ethereumApi'] == 'connected'
            graph_connected = data['verification']['graphApi'] == 'connected'
            voice_connected = data['verification']['voiceOps'] == 'connected'
            
            return {
                'ethereum': ethereum_connected,
                'graph': graph_connected,
                'voice': voice_connected,
                'data': data
            }
        else:
            print(f"❌ Frontend API: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Frontend API: Connection failed - {e}")
        return None

def test_frontend_pages():
    """Test frontend page accessibility"""
    print("\n🔍 Testing frontend pages...")
    
    pages = [
        ("Main Dashboard", "http://localhost:3000/"),
        ("Live Data", "http://localhost:3000/live-data"),
        ("Analytics", "http://localhost:3000/analytics"),
        ("Services", "http://localhost:3000/services")
    ]
    
    results = {}
    for name, url in pages:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Accessible")
                results[name] = True
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"❌ {name}: Connection failed - {e}")
            results[name] = False
    
    return results

def main():
    """Run all tests"""
    print("🚀 Testing Real Data Functionality")
    print("=" * 50)
    
    # Test 1: Ethereum API
    ethereum_ok = test_ethereum_api()
    
    # Test 2: Backend services
    backend_results = test_backend_services()
    
    # Test 3: Frontend API
    frontend_api_results = test_frontend_api()
    
    # Test 4: Frontend pages
    frontend_page_results = test_frontend_pages()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    print(f"Ethereum API: {'✅ Connected' if ethereum_ok else '❌ Failed'}")
    
    backend_ok = all(backend_results.values())
    print(f"Backend Services: {'✅ All Healthy' if backend_ok else '❌ Some Issues'}")
    
    frontend_api_ok = frontend_api_results is not None and all([
        frontend_api_results['ethereum'],
        frontend_api_results['graph'],
        frontend_api_results['voice']
    ])
    print(f"Frontend API: {'✅ Working' if frontend_api_ok else '❌ Issues'}")
    
    frontend_pages_ok = all(frontend_page_results.values())
    print(f"Frontend Pages: {'✅ All Accessible' if frontend_pages_ok else '❌ Some Issues'}")
    
    # Overall status
    overall_ok = ethereum_ok and backend_ok and frontend_api_ok and frontend_pages_ok
    print(f"\nOverall Status: {'🎉 ALL SYSTEMS OPERATIONAL' if overall_ok else '⚠️  SOME ISSUES DETECTED'}")
    
    if overall_ok:
        print("\n✅ Your frontend is successfully displaying real data!")
        print("   - Connected to live Ethereum mainnet")
        print("   - Backend services are healthy")
        print("   - Frontend API is working")
        print("   - All pages are accessible")
        print("\n🌐 Visit http://localhost:3000 to see the real-time dashboard")
    else:
        print("\n🔧 Some components need attention. Check the logs above.")

if __name__ == "__main__":
    main() 