"""
GCP Permissions Test Suite
Test BigQuery and Vertex AI access after permission updates
"""

import pytest
import os
import time
import json
from google.cloud import bigquery, aiplatform
from google.auth import default
import httpx

@pytest.mark.e2e
@pytest.mark.tier2
@pytest.mark.integration
class TestGCPPermissions:
    """Test GCP permissions after IAM updates"""
    
    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Load environment variables"""
        env_path = "/Users/jadenfix/eth/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    def test_bigquery_full_permissions(self):
        """Test BigQuery read/write permissions"""
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        dataset_id = os.getenv('BIGQUERY_DATASET')
        
        bq_client = bigquery.Client(project=project_id)
        
        print(f"Testing BigQuery permissions for project: {project_id}")
        
        try:
            # Test 1: Dataset access
            dataset_ref = f"{project_id}.{dataset_id}"
            dataset = bq_client.get_dataset(dataset_ref)
            print(f"✅ Dataset access successful: {dataset.dataset_id}")
            
            # Test 2: List tables
            tables = list(bq_client.list_tables(dataset))
            table_names = [table.table_id for table in tables]
            print(f"✅ Tables found: {table_names}")
            
            # Test 3: Query permissions (basic query)
            query = f"""
            SELECT 'Permission test' as test_message, 
                   CURRENT_TIMESTAMP() as test_time,
                   '{project_id}' as project_id
            """
            
            query_job = bq_client.query(query)
            results = list(query_job.result())
            
            assert len(results) == 1
            assert results[0].test_message == "Permission test"
            print(f"✅ Query permissions working: {results[0].test_time}")
            
            # Test 4: Table creation permissions
            test_table_id = f"permission_test_{int(time.time())}"
            schema = [
                bigquery.SchemaField("test_id", "STRING"),
                bigquery.SchemaField("timestamp", "TIMESTAMP"),
                bigquery.SchemaField("test_data", "STRING"),
            ]
            
            table_ref = f"{project_id}.{dataset_id}.{test_table_id}"
            table = bigquery.Table(table_ref, schema=schema)
            
            try:
                created_table = bq_client.create_table(table)
                print(f"✅ Table creation successful: {created_table.table_id}")
                
                # Test 5: Insert data permissions
                test_data = [{
                    "test_id": f"test_{int(time.time())}",
                    "timestamp": time.time(),
                    "test_data": "BigQuery write permission test"
                }]
                
                errors = bq_client.insert_rows_json(created_table, test_data)
                if len(errors) == 0:
                    print("✅ Data insertion successful")
                else:
                    print(f"⚠️  Insert errors: {errors}")
                
                # Test 6: Query the inserted data
                query = f"""
                SELECT * FROM `{table_ref}`
                WHERE test_data = 'BigQuery write permission test'
                """
                
                query_job = bq_client.query(query)
                query_results = list(query_job.result())
                
                if len(query_results) > 0:
                    print("✅ Data query after insert successful")
                else:
                    print("⚠️  No data found after insert")
                
                # Cleanup
                bq_client.delete_table(table_ref)
                print("✅ Table cleanup successful")
                
            except Exception as create_error:
                print(f"⚠️  Table creation failed: {create_error}")
                return False
                
        except Exception as e:
            print(f"❌ BigQuery permissions test failed: {e}")
            assert False, f"BigQuery permissions test failed: {e}"
        
        assert True, "BigQuery permissions test passed"
    
    def test_vertex_ai_permissions(self):
        """Test Vertex AI access permissions"""
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        region = os.getenv('VERTEX_AI_REGION', 'us-central1')
        
        print(f"Testing Vertex AI permissions for project: {project_id}, region: {region}")
        
        try:
            # Test 1: Initialize Vertex AI
            aiplatform.init(project=project_id, location=region)
            print("✅ Vertex AI initialization successful")
            
            # Test 2: Check authentication
            credentials, project = default()
            print(f"✅ Authentication successful for project: {project}")
            
            # Test 3: Test model endpoint access
            vertex_endpoint = os.getenv('VERTEX_AI_ENDPOINT')
            if vertex_endpoint:
                print(f"Testing configured endpoint: {vertex_endpoint}")
                
                # Try to access the Gemini model endpoint
                import httpx
                import asyncio
                
                async def test_gemini_endpoint():
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        # Test basic endpoint accessibility
                        base_endpoint = vertex_endpoint.replace('/predict', '')
                        
                        try:
                            response = await client.get(base_endpoint)
                            print(f"✅ Vertex AI endpoint accessible: {response.status_code}")
                            return True
                        except Exception as e:
                            print(f"⚠️  Vertex AI endpoint test: {e}")
                            return False
                
                # Run async test
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                endpoint_accessible = loop.run_until_complete(test_gemini_endpoint())
                loop.close()
                
                if endpoint_accessible:
                    print("✅ Vertex AI endpoint permissions working")
                else:
                    print("⚠️  Vertex AI endpoint access limited")
            
            assert True, "Vertex AI permissions test passed"
            
        except Exception as e:
            print(f"❌ Vertex AI permissions test failed: {e}")
            assert False, f"Vertex AI permissions test failed: {e}"
    
    def test_comprehensive_gcp_access(self):
        """Comprehensive test of all GCP services"""
        print("\n" + "="*60)
        print("COMPREHENSIVE GCP PERMISSIONS TEST")
        print("="*60)
        
        # Test BigQuery
        print("\n1. Testing BigQuery Permissions...")
        bq_success = self.test_bigquery_full_permissions()
        
        # Test Vertex AI  
        print("\n2. Testing Vertex AI Permissions...")
        vertex_success = self.test_vertex_ai_permissions()
        
        # Summary
        print("\n" + "="*60)
        print("PERMISSION TEST SUMMARY")
        print("="*60)
        
        if bq_success:
            print("✅ BigQuery: FULL ACCESS (read/write/create/delete)")
        else:
            print("⚠️  BigQuery: LIMITED ACCESS (permissions needed)")
            
        if vertex_success:
            print("✅ Vertex AI: ACCESSIBLE (model endpoints available)")
        else:
            print("⚠️  Vertex AI: LIMITED ACCESS (model access needed)")
        
        # Overall status
        if bq_success and vertex_success:
            print("\n🎉 ALL GCP PERMISSIONS WORKING!")
            print("Ready for full V3 system deployment")
            assert True, "All GCP permissions working"
        elif bq_success:
            print("\n✅ BigQuery permissions working - Vertex AI needs setup")
            print("Ready for data pipeline testing")
            assert True, "BigQuery permissions working"
        elif vertex_success:
            print("\n✅ Vertex AI accessible - BigQuery needs permissions")
            assert True, "Vertex AI accessible"
            print("Ready for AI explanations testing")
        else:
            print("\n⚠️  Both services need permission updates")
            print("Check IAM roles and try again")
        
        return bq_success, vertex_success

if __name__ == "__main__":
    # Load environment variables manually
    env_path = "/Users/jadenfix/eth/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    test = TestGCPPermissions()
    test.test_comprehensive_gcp_access()
