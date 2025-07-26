#!/usr/bin/env python3
"""
Test script to verify navigation functionality
"""
import requests
import time
from datetime import datetime

def test_navigation_pages():
    """Test all navigation pages to ensure they load correctly"""
    base_url = "http://localhost:3000"
    
    # Define all navigation pages to test
    pages = [
        ("Dashboard", "/"),
        ("Live Data", "/live-data"),
        ("MEV Intelligence", "/mev"),
        ("Entity Resolution", "/intelligence/entities"),
        ("Security & Compliance", "/compliance"),
        ("Analytics", "/analytics"),
        ("Visualization", "/canvas"),
        ("Voice Commands", "/voice"),
        ("System Monitoring", "/monitoring"),
        ("Settings", "/workspace"),
    ]
    
    print("🧭 Testing Navigation Pages")
    print("=" * 50)
    
    results = []
    
    for name, path in pages:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            results.append((name, path, response.status_code, status))
            print(f"{status} {name:20} - {path:25} (Status: {response.status_code})")
        except Exception as e:
            results.append((name, path, "ERROR", "❌"))
            print(f"❌ {name:20} - {path:25} (Error: {str(e)})")
        
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("📊 Navigation Test Summary")
    print("=" * 50)
    
    successful = sum(1 for _, _, status, _ in results if status == 200)
    total = len(results)
    
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")
    print(f"📈 Success Rate: {(successful/total)*100:.1f}%")
    
    if successful == total:
        print("\n🎉 All navigation pages are working correctly!")
    else:
        print("\n⚠️ Some pages failed to load. Check the errors above.")
    
    return results

def test_navigation_content():
    """Test that pages have meaningful content"""
    print("\n🔍 Testing Page Content")
    print("=" * 50)
    
    base_url = "http://localhost:3000"
    
    # Test a few key pages for content
    content_tests = [
        ("Dashboard", "/", ["Welcome", "Command Center", "LIVE DATA"]),
        ("Live Data", "/live-data", ["Current Block", "Transactions", "Real-time"]),
        ("MEV Intelligence", "/mev", ["MEV", "Front-running", "Arbitrage"]),
        ("Analytics", "/analytics", ["Analytics", "Charts", "Metrics"]),
    ]
    
    for name, path, expected_content in content_tests:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                found_content = [word for word in expected_content if word.lower() in content]
                if found_content:
                    print(f"✅ {name:20} - Contains expected content: {', '.join(found_content)}")
                else:
                    print(f"⚠️ {name:20} - Missing expected content")
            else:
                print(f"❌ {name:20} - Failed to load (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name:20} - Error: {str(e)}")

if __name__ == "__main__":
    print(f"🚀 Starting Navigation Tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test page accessibility
    results = test_navigation_pages()
    
    # Test page content
    test_navigation_content()
    
    print(f"\n✅ Navigation testing completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 