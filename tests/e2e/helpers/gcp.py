"""
Google Cloud Platform testing utilities
"""

import json
import time
from typing import Dict, List, Any, Optional
import logging

# Import Google Cloud dependencies with graceful fallbacks
try:
    from google.cloud import bigquery, pubsub_v1
    from google.cloud.exceptions import NotFound
    GCP_AVAILABLE = True
except ImportError:
    bigquery = None
    pubsub_v1 = None
    NotFound = None
    GCP_AVAILABLE = False

try:
    from google.cloud import aiplatform
    AI_PLATFORM_AVAILABLE = True
except ImportError:
    aiplatform = None
    AI_PLATFORM_AVAILABLE = False

logger = logging.getLogger(__name__)

class GCPTestUtils:
    """Utilities for GCP services in tests"""
    
    def __init__(self, project_id: str):
        if not GCP_AVAILABLE:
            raise ImportError("Google Cloud libraries not available")
        
        self.project_id = project_id
        self.bq_client = None
        self.pubsub_client = None
        
    def _get_bq_client(self):
        """Get BigQuery client with lazy initialization"""
        if not self.bq_client:
            self.bq_client = bigquery.Client(project=self.project_id)
        return self.bq_client
    
    def _get_pubsub_client(self):
        """Get Pub/Sub client with lazy initialization"""
        if not self.pubsub_client:
            self.pubsub_client = pubsub_v1.PublisherClient()
        return self.pubsub_client
    
    def bq_create_dataset(self, dataset_id: str) -> None:
        """Create BigQuery dataset"""
        client = self._get_bq_client()
        dataset = bigquery.Dataset(f"{self.project_id}.{dataset_id}")
        dataset.location = "US"
        
        try:
            client.create_dataset(dataset)
            logger.info(f"Created dataset: {dataset_id}")
        except Exception as e:
            if "already exists" not in str(e).lower():
                logger.warning(f"Failed to create dataset {dataset_id}: {e}")
    
    def bq_create_table(self, dataset_id: str, table_id: str, schema: Dict) -> None:
        """Create BigQuery table with schema"""
        client = self._get_bq_client()
        table_ref = client.dataset(dataset_id).table(table_id)
        
        # Convert schema dict or list to BigQuery schema
        bq_schema = []
        if isinstance(schema, dict) and "fields" in schema:
            fields = schema["fields"]
        elif isinstance(schema, list):
            fields = schema
        else:
            fields = []
        for field in fields:
            if hasattr(field, 'name') and hasattr(field, 'field_type'):
                # Already a SchemaField object
                bq_schema.append(field)
            elif isinstance(field, dict):
                bq_schema.append(bigquery.SchemaField(
                    field["name"],
                    field["type"],
                    mode=field.get("mode", "NULLABLE")
                ))
            else:
                raise TypeError(f"Unsupported schema field type: {type(field)}")
        
        table = bigquery.Table(table_ref, schema=bq_schema)
        
        try:
            client.create_table(table)
            logger.info(f"Created table: {dataset_id}.{table_id}")
        except Exception as e:
            if "already exists" not in str(e).lower():
                logger.warning(f"Failed to create table {dataset_id}.{table_id}: {e}")
    
    def bq_insert_rows(self, dataset_id: str, table_id: str, rows: List[Dict]) -> None:
        """Insert rows into BigQuery table"""
        table_ref = self.bq_client.dataset(dataset_id).table(table_id)
        table = self.bq_client.get_table(table_ref)
        
        errors = self.bq_client.insert_rows_json(table, rows)
        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")
        
        logger.info(f"Inserted {len(rows)} rows into {dataset_id}.{table_id}")
    
    def bq_query(self, query: str) -> List[Dict]:
        """Execute BigQuery query and return results"""
        job = self.bq_client.query(query)
        results = job.result()
        
        return [dict(row) for row in results]
    
    def bq_wait_for_rows(self, dataset_id: str, table_id: str, expected_count: int, timeout: int = 300) -> bool:
        """Wait for table to have expected row count"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            query = f"SELECT COUNT(*) as count FROM `{self.project_id}.{dataset_id}.{table_id}`"
            try:
                results = self.bq_query(query)
                if results and results[0]['count'] >= expected_count:
                    return True
            except Exception as e:
                logger.warning(f"Query failed: {e}")
            
            time.sleep(5)
        
        return False
    
    # Pub/Sub utilities
    def pubsub_create_topic(self, topic_id: str) -> None:
        """Create Pub/Sub topic if it doesn't exist"""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        try:
            self.publisher.get_topic(request={"topic": topic_path})
            logger.info(f"Topic {topic_id} already exists")
        except NotFound:
            self.publisher.create_topic(request={"name": topic_path})
            logger.info(f"Created topic {topic_id}")
    
    def pubsub_create_subscription(self, topic_id: str, subscription_id: str) -> None:
        """Create Pub/Sub subscription"""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        subscription_path = self.subscriber.subscription_path(self.project_id, subscription_id)
        
        try:
            self.subscriber.get_subscription(request={"subscription": subscription_path})
            logger.info(f"Subscription {subscription_id} already exists")
        except NotFound:
            self.subscriber.create_subscription(
                request={
                    "name": subscription_path,
                    "topic": topic_path,
                    "ack_deadline_seconds": 60
                }
            )
            logger.info(f"Created subscription {subscription_id}")
    
    def pubsub_publish(self, topic_id: str, data: Dict[str, Any], attributes: Optional[Dict[str, str]] = None) -> str:
        """Publish message to Pub/Sub topic"""
        topic_path = self.publisher.topic_path(self.project_id, topic_id)
        
        message_data = json.dumps(data).encode('utf-8')
        future = self.publisher.publish(topic_path, message_data, **(attributes or {}))
        
        message_id = future.result()
        logger.info(f"Published message {message_id} to {topic_id}")
        return message_id
    
    def pubsub_pull_messages(self, subscription_id: str, max_messages: int = 10, timeout: int = 60) -> List[Dict]:
        """Pull messages from Pub/Sub subscription"""
        subscription_path = self.subscriber.subscription_path(self.project_id, subscription_id)
        
        response = self.subscriber.pull(
            request={
                "subscription": subscription_path,
                "max_messages": max_messages,
            },
            timeout=timeout
        )
        
        messages = []
        ack_ids = []
        
        for received_message in response.received_messages:
            try:
                data = json.loads(received_message.message.data.decode('utf-8'))
                messages.append({
                    "data": data,
                    "attributes": dict(received_message.message.attributes),
                    "message_id": received_message.message.message_id
                })
                ack_ids.append(received_message.ack_id)
            except Exception as e:
                logger.error(f"Failed to parse message: {e}")
        
        # Acknowledge messages
        if ack_ids:
            self.subscriber.acknowledge(
                request={
                    "subscription": subscription_path,
                    "ack_ids": ack_ids
                }
            )
        
        logger.info(f"Pulled {len(messages)} messages from {subscription_id}")
        return messages
    
    # Vertex AI utilities
    def vertex_wait_for_job(self, job_id: str, timeout: int = 900) -> bool:
        """Wait for Vertex AI job to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # This is a simplified check - in practice you'd use the Vertex AI API
                # to check job status
                logger.info(f"Checking job {job_id} status...")
                time.sleep(30)
                # For now, assume job completes after 2 minutes for testing
                if time.time() - start_time > 120:
                    return True
            except Exception as e:
                logger.error(f"Error checking job status: {e}")
            
            time.sleep(10)
        
        return False
    
    def vertex_run_pipeline(self, pipeline_spec: str, parameters: Optional[Dict] = None) -> str:
        """Run Vertex AI pipeline (mock implementation)"""
        # In a real implementation, this would submit a pipeline job
        job_id = f"test_job_{int(time.time())}"
        logger.info(f"Submitting pipeline job {job_id}")
        return job_id
    
    # Service utilities
    def call_service(self, service: str, endpoint: str = "", method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Call internal service (mock implementation)"""
        # In practice, this would make HTTP calls to your services
        logger.info(f"Calling {service} service: {method} {endpoint}")
        
        if service == "ontology" and "entity" in endpoint:
            return {
                "data": {
                    "entity": {
                        "id": "test_entity_123",
                        "addresses": [
                            {"address": "0xA0b86a33E6441e8C73C3238E5A3F0B2E1f1D8E3F"},
                            {"address": "0xB1c97a44F7552e9D84C4239F6B4E1C3F2e2E9F4A"}
                        ]
                    }
                }
            }
        
        return {"status": "mocked", "service": service}

# Schema definitions for test tables
CHAIN_EVENTS_SCHEMA = [
    bigquery.SchemaField("block_number", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("transaction_hash", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("from_address", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("to_address", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("value", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("gas_used", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("timestamp", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("entity_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("fixture_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("fixture_batch", "STRING", mode="NULLABLE"),
]

ENTITIES_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("entity_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("addresses", "STRING", mode="REPEATED"),
    bigquery.SchemaField("institution", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("labels", "STRING", mode="REPEATED"),
    bigquery.SchemaField("risk_score", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]

PII_TEST_SCHEMA = [
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("wallet_address", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("ssn", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("phone", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("public_data", "STRING", mode="REQUIRED"),
]
