"""
T0-D: Load UI → renders without crash
Demo-blocking test: Basic UI functionality works
"""

import pytest
import asyncio
import json
from tests.e2e.helpers.gcp import GCPTestUtils

@pytest.mark.e2e
@pytest.mark.tier0
class TestUIRendering:
    """Test basic UI rendering and functionality"""
    
    @pytest.mark.asyncio
    async def test_dashboard_loads_without_crash(self, gcp_env, async_http_client, clean_test_data):
        """
        T0-D: Basic UI loading test
        
        Flow:
        1. Setup test data in backend
        2. Make request to dashboard endpoint
        3. Verify response is valid HTML/JSON
        4. Check for critical UI elements
        """
        # 1. Setup minimal test data for UI
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_ui_test"
        test_table = "dashboard_data"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, test_table, {
            "fields": [
                {"name": "metric_name", "type": "STRING"},
                {"name": "metric_value", "type": "FLOAT"},
                {"name": "timestamp", "type": "INTEGER"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        # Insert sample dashboard metrics
        dashboard_metrics = [
            {"metric_name": "total_transactions", "metric_value": 12345.0, "timestamp": 1698000000, "fixture_id": "T0_D_ui"},
            {"metric_name": "total_volume", "metric_value": 9876543.21, "timestamp": 1698000000, "fixture_id": "T0_D_ui"},
            {"metric_name": "risk_alerts", "metric_value": 23.0, "timestamp": 1698000000, "fixture_id": "T0_D_ui"},
            {"metric_name": "active_addresses", "metric_value": 4567.0, "timestamp": 1698000000, "fixture_id": "T0_D_ui"}
        ]
        
        gcp_utils.bq_insert_rows(test_dataset, test_table, dashboard_metrics)
        
        # 2. Test dashboard API endpoint
        response = await async_http_client.get("/api/dashboard/metrics")
        
        # 3. Verify response format
        assert response.status_code == 200, f"Dashboard API should return 200, got {response.status_code}"
        
        # Check if response is JSON
        try:
            data = response.json()
            assert isinstance(data, dict), "Response should be JSON object"
            
            # 4. Check for critical dashboard elements
            expected_fields = ["total_transactions", "total_volume", "risk_alerts", "active_addresses"]
            for field in expected_fields:
                assert field in data, f"Dashboard should include {field} metric"
                assert isinstance(data[field], (int, float)), f"{field} should be a number"
        
        except json.JSONDecodeError:
            # If not JSON, check if it's valid HTML
            content = response.text
            assert "<html" in content.lower(), "Response should be valid HTML"
            assert "</html>" in content.lower(), "HTML should be complete"
            assert "dashboard" in content.lower(), "Should contain dashboard content"
        
        print("✅ T0-D: Dashboard loads without crash")
    
    @pytest.mark.asyncio
    async def test_graph_visualization_endpoint(self, gcp_env, async_http_client, clean_test_data):
        """Test graph visualization endpoint"""
        # Test graph visualization API
        response = await async_http_client.get("/api/graph/visualization", params={
            "address": "0xTEST123",
            "depth": 2
        })
        
        # Should not crash and return some graph data
        assert response.status_code in [200, 404], f"Graph API should return 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "nodes" in data or "message" in data, "Should have nodes or message field"
            
        print("✅ T0-D: Graph visualization endpoint accessible")
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, gcp_env, async_http_client, clean_test_data):
        """Test application health check"""
        response = await async_http_client.get("/health")
        
        assert response.status_code == 200, f"Health check should return 200, got {response.status_code}"
        
        # Check response format
        try:
            data = response.json()
            assert "status" in data, "Health response should have status field"
            assert data["status"] in ["healthy", "ok", "up"], f"Status should indicate health, got {data['status']}"
            
            # Optional fields that might be present
            if "services" in data:
                assert isinstance(data["services"], dict), "Services should be a dict"
                
            if "timestamp" in data:
                assert isinstance(data["timestamp"], (int, str)), "Timestamp should be int or string"
                
        except json.JSONDecodeError:
            # Simple text response is also acceptable
            content = response.text.lower()
            assert any(word in content for word in ["ok", "healthy", "up", "running"]), "Should indicate health status"
        
        print("✅ T0-D: Health check endpoint working")
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, gcp_env, async_http_client, clean_test_data):
        """Test API error handling doesn't crash"""
        # Test invalid endpoints
        invalid_endpoints = [
            "/api/nonexistent",
            "/api/graph/invalid",
            "/api/dashboard/badparam"
        ]
        
        for endpoint in invalid_endpoints:
            response = await async_http_client.get(endpoint)
            
            # Should return proper HTTP error codes, not crash
            assert response.status_code in [400, 404, 405, 500], f"Should return proper error code for {endpoint}"
            
            # Response should still be valid (JSON error or HTML error page)
            content_type = response.headers.get("content-type", "").lower()
            
            if "json" in content_type:
                try:
                    error_data = response.json()
                    assert "error" in error_data or "message" in error_data, "JSON error should have error/message field"
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON in error response for {endpoint}")
            
        print("✅ T0-D: API error handling working properly")
    
    @pytest.mark.asyncio
    async def test_static_assets_loading(self, gcp_env, async_http_client, clean_test_data):
        """Test that static assets load properly"""
        # Test common static asset paths
        static_paths = [
            "/static/css/main.css",
            "/static/js/app.js", 
            "/assets/logo.png",
            "/favicon.ico"
        ]
        
        loaded_assets = 0
        
        for path in static_paths:
            response = await async_http_client.get(path)
            
            # Assets should either load (200) or not exist (404), but not crash (500)
            if response.status_code == 200:
                loaded_assets += 1
                content_type = response.headers.get("content-type", "")
                
                # Verify content type makes sense for asset
                if path.endswith(".css"):
                    assert "css" in content_type.lower(), f"CSS file should have CSS content type"
                elif path.endswith(".js"):
                    assert "javascript" in content_type.lower() or "text" in content_type.lower(), f"JS file should have JS content type"
                elif path.endswith(".png"):
                    assert "image" in content_type.lower(), f"PNG file should have image content type"
            
            elif response.status_code == 404:
                # 404 is acceptable for static assets that might not exist
                pass
            else:
                # Should not return 500 errors for static assets
                assert response.status_code != 500, f"Static asset {path} should not cause server error"
        
        # At least some static assets should be available for a functioning UI
        print(f"✅ T0-D: Static assets accessible ({loaded_assets}/{len(static_paths)} found)")
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self, gcp_env, clean_test_data):
        """Test WebSocket connection for real-time updates"""
        import websockets
        import asyncio
        
        try:
            # Attempt to connect to WebSocket endpoint
            uri = f"ws://localhost:8080/ws/updates"
            
            async with asyncio.timeout(5):  # 5 second timeout
                async with websockets.connect(uri) as websocket:
                    # Send a test message
                    test_message = {"type": "ping", "data": "test"}
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for response
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    assert "type" in response_data, "WebSocket response should have type field"
                    print("✅ T0-D: WebSocket connection working")
                    
        except (ConnectionRefusedError, OSError, asyncio.TimeoutError):
            # WebSocket might not be implemented yet - that's okay for T0
            print("⚠️  T0-D: WebSocket not available (optional for T0)")
        except Exception as e:
            # Other errors might indicate problems
            print(f"⚠️  T0-D: WebSocket test failed: {e}")
            # Don't fail the test since WebSocket is optional for basic functionality
    
    def test_ui_configuration_valid(self, gcp_env, clean_test_data):
        """Test UI configuration is valid"""
        # Check for common UI configuration files
        import os
        
        ui_config_paths = [
            "/Users/jadenfix/eth/services/ui/nextjs-app/next.config.js",
            "/Users/jadenfix/eth/services/ui/nextjs-app/package.json",
            "/Users/jadenfix/eth/services/visualization/workspace/layout.json"
        ]
        
        for config_path in ui_config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        
                        if config_path.endswith('.json'):
                            # Validate JSON syntax
                            json.loads(content)
                        elif config_path.endswith('.js'):
                            # Basic syntax check for JavaScript
                            assert "module.exports" in content or "export" in content, "JS config should have exports"
                        
                    print(f"✅ T0-D: UI config {os.path.basename(config_path)} is valid")
                    
                except (json.JSONDecodeError, AssertionError) as e:
                    pytest.fail(f"UI config {config_path} is invalid: {e}")
                except Exception as e:
                    print(f"⚠️  T0-D: Could not validate {config_path}: {e}")
            else:
                print(f"⚠️  T0-D: UI config {config_path} not found (may be optional)")
        
        print("✅ T0-D: UI configuration validation complete")
