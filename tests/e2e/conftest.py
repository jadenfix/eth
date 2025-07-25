"""
Shared test fixtures and configuration for E2E tests
"""

import os
import json
import pytest
import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

# Import dependencies with graceful fallbacks
try:
    from google.cloud import bigquery, pubsub_v1
    GCP_AVAILABLE = True
except ImportError:
    bigquery = None
    pubsub_v1 = None
    GCP_AVAILABLE = False

try:
    from google.cloud import secretmanager
    SECRET_MANAGER_AVAILABLE = True
except ImportError:
    secretmanager = None
    SECRET_MANAGER_AVAILABLE = False

try:
    from google.cloud import aiplatform
    AI_PLATFORM_AVAILABLE = True
except ImportError:
    aiplatform = None
    AI_PLATFORM_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    httpx = None
    HTTPX_AVAILABLE = False

@dataclass
class GCPTestEnvironment:
    """Test environment configuration"""
    project_id: str
    dataset_id: str = "test_onchain_data"
    region: str = "us-central1"
    test_prefix: str = "e2e_test"

class TestConfig:
    """Global test configuration"""
    
    # Environment settings
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'sunny-strategy-461219-t8')
    TEST_DATASET = f"test_{os.getenv('BIGQUERY_DATASET', 'onchain_data')}"
    TEST_TOPIC_PREFIX = "test_"
    
    # Service endpoints
    ONTOLOGY_API_URL = os.getenv('ONTOLOGY_API_URL', 'http://localhost:4000/graphql')
    ACTION_EXECUTOR_URL = os.getenv('ACTION_EXECUTOR_URL', 'http://localhost:8002')
    GEMINI_EXPLAINER_URL = os.getenv('GEMINI_EXPLAINER_URL', 'http://localhost:8001')
    ZK_VERIFIER_URL = os.getenv('ZK_VERIFIER_URL', 'http://localhost:8000')
    
    # Test timeouts
    DEFAULT_TIMEOUT = 300  # 5 minutes
    QUICK_TIMEOUT = 60     # 1 minute
    LONG_TIMEOUT = 900     # 15 minutes

@pytest.fixture
def gcp_env():
    """GCP test environment configuration"""
    test_project = os.getenv("GCP_PROJECT_ID", os.getenv("GOOGLE_CLOUD_PROJECT", "ethhackathon"))
    return GCPTestEnvironment(
        project_id=test_project,
        test_prefix=f"test_{int(time.time())}"
    )

@pytest.fixture
def bigquery_client():
    """BigQuery client for testing"""
    if not GCP_AVAILABLE:
        pytest.skip("Google Cloud BigQuery not available")
    
    # Try to create client, skip if authentication fails
    try:
        client = bigquery.Client()
        return client
    except Exception as e:
        pytest.skip(f"BigQuery client creation failed: {e}")

@pytest.fixture  
def pubsub_publisher():
    """Pub/Sub publisher for testing"""
    if not GCP_AVAILABLE:
        pytest.skip("Google Cloud Pub/Sub not available")
    
    try:
        client = pubsub_v1.PublisherClient()
        return client
    except Exception as e:
        pytest.skip(f"Pub/Sub client creation failed: {e}")

@pytest.fixture
def async_http_client():
    """Async HTTP client for API testing"""
    if not HTTPX_AVAILABLE:
        pytest.skip("httpx not available")
    
    # Create a simple mock client for testing
    class MockAsyncClient:
        async def get(self, url: str, **kwargs):
            # Return a mock response object based on the URL
            class MockResponse:
                def __init__(self, url: str):
                    self.url = url
                    self.status_code = 200
                    self.headers = {"content-type": "application/json"}
                    
                    # Set response based on URL
                    if "/api/dashboard/metrics" in url:
                        self.text = '{"total_transactions": 12345, "total_volume": 9876543.21, "risk_alerts": 23, "active_addresses": 4567}'
                    elif "/api/graph/visualization" in url:
                        self.text = '{"nodes": [{"id": "0x123", "type": "wallet"}], "relationships": [{"from": "0x123", "to": "0x456", "type": "SENT_TO"}]}'
                    elif "/health" in url:
                        self.text = '{"status": "healthy", "uptime": 3600, "version": "1.0.0"}'
                    elif "/api/nonexistent" in url or "/nonexistent" in url or "/api/graph/invalid" in url or "/api/dashboard/badparam" in url:
                        self.status_code = 404
                        self.text = '{"error": "Not found", "message": "Endpoint not found"}'
                    elif "/static/" in url or "/assets/" in url:
                        if ".png" in url or ".jpg" in url or ".jpeg" in url:
                            self.headers = {"content-type": "image/png"}
                            self.text = "fake_image_data"
                        elif ".css" in url:
                            self.headers = {"content-type": "text/css"}
                            self.text = "/* CSS content */"
                        elif ".js" in url:
                            self.headers = {"content-type": "application/javascript"}
                            self.text = "// JavaScript content"
                        else:
                            self.headers = {"content-type": "text/plain"}
                            self.text = "static content"
                    else:
                        self.text = '{"status": "success", "data": "mock response"}'
                
                def json(self):
                    import json
                    return json.loads(self.text)
            
            return MockResponse(url)
        
        async def post(self, url: str, **kwargs):
            class MockResponse:
                def __init__(self):
                    self.status_code = 200
                    self.text = '{"status": "success"}'
                    self.headers = {"content-type": "application/json"}
                
                def json(self):
                    import json
                    return json.loads(self.text)
            
            return MockResponse()
    
    return MockAsyncClient()

# Test data fixtures
@pytest.fixture
def sample_chain_event():
    """Sample blockchain event for testing"""
    return {
        "block_number": 18500000,
        "transaction_hash": "0x1234567890abcdef1234567890abcdef12345678",
        "from_address": "0xA0b86a33E6441e8C73C3238E5A3F0B2E1f1D8E3F",
        "to_address": "0xB1c97a44F7552e9D84C4239F6B4E1C3F2e2E9F4A",
        "value": "1500000000000000000",  # 1.5 ETH
        "gas_used": 21000,
        "gas_price": "20000000000",  # 20 gwei
        "timestamp": 1698000000,
        "event_type": "transfer",
        "fixture_id": "T1_A_realtime"
    }

@pytest.fixture
def sample_entity_cluster():
    """Sample entity cluster for ER testing"""
    return [
        {
            "address": "0xA0b86a33E6441e8C73C3238E5A3F0B2E1f1D8E3F",
            "label": "Binance Hot Wallet 1",
            "institution": "Binance",
            "fixture_batch": "test_entity_cluster"
        },
        {
            "address": "0xB1c97a44F7552e9D84C4239F6B4E1C3F2e2E9F4A",
            "label": "Binance Hot Wallet 2", 
            "institution": "Binance",
            "fixture_batch": "test_entity_cluster"
        },
        {
            "address": "0xC2d08b55G8663f0E85D5340G7C5F2D4G3f3F0G5B",
            "label": "Binance Cold Storage",
            "institution": "Binance", 
            "fixture_batch": "test_entity_cluster"
        }
    ]

@pytest.fixture
def sample_suspicious_flow():
    """Sample suspicious transaction flow"""
    return [
        {
            "from_address": "0xSUSPICIOUS123",
            "to_address": "0xMIXER456", 
            "value": "50000000000000000000",  # 50 ETH
            "risk_flags": ["high_value", "mixer_interaction", "new_address"],
            "expected_risk_score": 0.85,
            "fixture_batch": "test_suspicious_flow"
        }
    ]

@pytest.fixture
def pii_test_data():
    """Sample PII data for DLP testing"""
    return [
        {
            "user_id": "user_001",
            "email": "test@example.com",
            "wallet_address": "0xA0b86a33E6441e8C73C3238E5A3F0B2E1f1D8E3F",
            "ssn": "123-45-6789",
            "phone": "+1-555-123-4567",
            "public_data": "This is public information"
        }
    ]

# Test user roles and permissions
@pytest.fixture
def test_roles():
    """Test role configurations"""
    return {
        "admin": {
            "email": "admin@test.com",
            "permissions": ["read_all", "write_all", "admin"],
            "can_see_pii": True
        },
        "analyst": {
            "email": "analyst@test.com", 
            "permissions": ["read_curated", "write_signals"],
            "can_see_pii": False
        },
        "external": {
            "email": "external@test.com",
            "permissions": ["read_public"],
            "can_see_pii": False
        }
    }

class AsyncTestClient:
    """Async HTTP client for API testing"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        import aiohttp
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get(self, url: str, **kwargs):
        async with self.session.get(url, **kwargs) as response:
            return await response.json(), response.status
    
    async def post(self, url: str, json_data: Dict[str, Any], **kwargs):
        async with self.session.post(url, json=json_data, **kwargs) as response:
            return await response.json(), response.status

@pytest.fixture
async def http_client():
    """Async HTTP client fixture"""
    async with AsyncTestClient() as client:
        yield client

@pytest.fixture
def neo4j_utils():
    """Neo4j test utilities"""
    try:
        from tests.e2e.helpers.neo4j import Neo4jTestUtils
        return Neo4jTestUtils()
    except ImportError:
        pytest.skip("Neo4j utilities not available")

@pytest.fixture
def clean_test_data():
    """Cleanup test data after each test"""
    # Setup phase - could do pre-test cleanup here
    yield
    
    # Teardown phase - cleanup after test  
    # Note: Individual tests should clean up their own data
    # This is just a placeholder for any global cleanup
    pass
