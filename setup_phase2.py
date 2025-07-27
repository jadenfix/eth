#!/usr/bin/env python3
"""
Phase 2 Setup Script
Installs dependencies and configures environment for Entity Resolution & Graph Database
"""

import subprocess
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result"""
    logger.info(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    logger.info("🐍 Checking Python version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("❌ Python 3.8+ is required")
        return False
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python dependencies"""
    logger.info("📦 Installing Python dependencies")
    
    # Upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def setup_environment():
    """Setup environment variables"""
    logger.info("🔧 Setting up environment variables")
    
    env_file = Path(".env")
    if not env_file.exists():
        logger.info("Creating .env file")
        env_content = """# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# API Configuration
API_HOST=0.0.0.0
API_PORT=4000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:4000
NEXT_PUBLIC_WS_URL=ws://localhost:4000

# Development Configuration
DEBUG=true
LOG_LEVEL=INFO
"""
        env_file.write_text(env_content)
        logger.info("✅ .env file created")
    else:
        logger.info("✅ .env file already exists")
    
    return True

def check_ports():
    """Check if required ports are available"""
    logger.info("🔌 Checking port availability")
    
    import socket
    
    ports_to_check = [4000, 3000, 4001]
    unavailable_ports = []
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            logger.info(f"✅ Port {port} is available")
        except OSError:
            unavailable_ports.append(port)
            logger.warning(f"⚠️ Port {port} is in use")
    
    if unavailable_ports:
        logger.warning(f"Ports {unavailable_ports} are in use. You may need to stop other services.")
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("🧪 Testing module imports")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'neo4j',
        'numpy',
        'pandas',
        'sklearn',
        'networkx',
        'aiohttp',
        'strawberry'
    ]
    
    failed_imports = []
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module} imported successfully")
        except ImportError as e:
            failed_imports.append(module)
            logger.error(f"❌ Failed to import {module}: {e}")
    
    if failed_imports:
        logger.error(f"❌ Failed to import: {failed_imports}")
        return False
    
    return True

def create_test_data():
    """Create test data for Phase 2"""
    logger.info("📊 Creating test data")
    
    test_data_dir = Path("test_data")
    test_data_dir.mkdir(exist_ok=True)
    
    # Create sample transactions
    sample_transactions = [
        {
            "hash": "0x1234567890abcdef",
            "from": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "value": 1.5,
            "gasPrice": 25,
            "gasUsed": 21000,
            "blockNumber": 18000000,
            "timestamp": 1700000000,
            "status": True,
            "chainId": 1,
            "input": "0x"
        },
        {
            "hash": "0xabcdef1234567890",
            "from": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "to": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
            "value": 0.5,
            "gasPrice": 30,
            "gasUsed": 21000,
            "blockNumber": 18000001,
            "timestamp": 1700000060,
            "status": True,
            "chainId": 1,
            "input": "0x"
        }
    ]
    
    import json
    with open(test_data_dir / "sample_transactions.json", "w") as f:
        json.dump(sample_transactions, f, indent=2)
    
    logger.info("✅ Test data created")
    return True

def run_quick_tests():
    """Run quick tests to verify setup"""
    logger.info("🧪 Running quick tests")
    
    # Test Graph API server startup
    try:
        import uvicorn
        from services.graph_api.graphql_server import app
        
        logger.info("✅ Graph API server can be imported")
        
        # Test entity resolution
        from services.entity_resolution.entity_resolver import EntityResolver
        resolver = EntityResolver()
        logger.info("✅ Entity resolver can be instantiated")
        
        # Test Neo4j client
        from services.graph_api.neo4j_client import Neo4jClient
        client = Neo4jClient()
        logger.info("✅ Neo4j client can be instantiated")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Quick tests failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting Phase 2 Setup")
    logger.info("=" * 60)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("Check Ports", check_ports),
        ("Test Imports", test_imports),
        ("Create Test Data", create_test_data),
        ("Quick Tests", run_quick_tests)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        logger.info(f"\n📋 Step: {step_name}")
        if not step_func():
            failed_steps.append(step_name)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 SETUP SUMMARY")
    logger.info("=" * 60)
    
    if not failed_steps:
        logger.info("🎉 All setup steps completed successfully!")
        logger.info("✅ Phase 2 is ready for testing")
        logger.info("\n📋 Next steps:")
        logger.info("1. Start Neo4j database (if not already running)")
        logger.info("2. Run: python comprehensive_phase2_test.py")
        logger.info("3. Start Graph API: uvicorn services.graph_api.graphql_server:app --host 0.0.0.0 --port 4000")
        logger.info("4. Start Frontend: cd services/ui/nextjs-app && npm run dev")
    else:
        logger.error(f"❌ Setup failed for steps: {failed_steps}")
        logger.error("Please fix the issues and run setup again")
        return 1
    
    logger.info("=" * 60)
    return 0

if __name__ == "__main__":
    exit(main()) 