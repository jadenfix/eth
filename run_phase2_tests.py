#!/usr/bin/env python3
"""
Phase 2 Test Runner
Runs all Phase 2 tests and provides comprehensive status report
"""

import asyncio
import subprocess
import sys
import os
import time
import json
from datetime import datetime

def run_setup():
    """Run Phase 2 setup"""
    print("🔄 Running Phase 2 setup...")
    result = subprocess.run([sys.executable, "setup_phase2.py"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Setup completed successfully")
        return True
    else:
        print("❌ Setup failed")
        print(result.stderr)
        return False

def run_comprehensive_tests():
    """Run comprehensive Phase 2 tests"""
    print("🔄 Running comprehensive Phase 2 tests...")
    result = subprocess.run([sys.executable, "comprehensive_phase2_test.py"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Comprehensive tests completed")
        return True
    else:
        print("❌ Comprehensive tests failed")
        print(result.stderr)
        return False

def check_services():
    """Check if required services are running"""
    print("🔍 Checking service status...")
    
    import socket
    
    services = {
        "Graph API (Port 4000)": 4000,
        "Frontend (Port 3000)": 3000,
        "Access Control (Port 4001)": 4001
    }
    
    running_services = []
    for service_name, port in services.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('localhost', port))
            sock.close()
            running_services.append(service_name)
            print(f"✅ {service_name} is running")
        except:
            print(f"❌ {service_name} is not running")
    
    return running_services

def generate_status_report():
    """Generate comprehensive status report"""
    print("\n" + "="*80)
    print("📊 PHASE 2 IMPLEMENTATION STATUS REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check services
    running_services = check_services()
    
    # Check files
    required_files = [
        "services/graph_api/graphql_server.py",
        "services/entity_resolution/entity_resolver.py",
        "services/entity_resolution/pipeline.py",
        "services/graph_api/neo4j_client.py",
        "services/ethereum_ingester/real_data_service.py",
        "requirements.txt",
        ".env"
    ]
    
    print("\n📁 File Status:")
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
    
    # Check dependencies
    print("\n📦 Dependency Status:")
    dependencies = [
        'fastapi', 'uvicorn', 'neo4j', 'numpy', 'pandas', 
        'scikit-learn', 'networkx', 'aiohttp', 'strawberry'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - NOT INSTALLED")
    
    # Service status
    print(f"\n🔌 Service Status:")
    print(f"Running services: {len(running_services)}/{len(services)}")
    for service in running_services:
        print(f"✅ {service}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if len(running_services) < 3:
        print("1. Start missing services:")
        if "Graph API (Port 4000)" not in running_services:
            print("   - Run: uvicorn services.graph_api.graphql_server:app --host 0.0.0.0 --port 4000")
        if "Frontend (Port 3000)" not in running_services:
            print("   - Run: cd services/ui/nextjs-app && npm run dev")
        if "Access Control (Port 4001)" not in running_services:
            print("   - Run: cd services/access_control && python main.py")
    
    print("2. Run comprehensive tests: python comprehensive_phase2_test.py")
    print("3. Check Neo4j connection if entity resolution is failing")
    
    print("="*80)

def main():
    """Main function"""
    print("🚀 Phase 2 Test Runner")
    print("="*50)
    
    # Step 1: Setup
    if not run_setup():
        print("❌ Setup failed. Please fix issues and try again.")
        return 1
    
    # Step 2: Run tests
    if not run_comprehensive_tests():
        print("❌ Tests failed. Please check the output above.")
        return 1
    
    # Step 3: Generate status report
    generate_status_report()
    
    print("\n🎉 Phase 2 test runner completed!")
    return 0

if __name__ == "__main__":
    exit(main()) 