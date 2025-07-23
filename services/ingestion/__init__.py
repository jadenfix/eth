"""
Ingestion Layer - BigQuery CDC Event Publisher

Publishes row-level change events from BigQuery to Pub/Sub for 
bidirectional sync with Neo4j.
"""

import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

import structlog
from google.cloud import pubsub_v1
from google.cloud import bigquery

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class BigQueryCDCPublisher:
    """Publishes BigQuery row changes to Pub/Sub for Neo4j sync"""
    
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.publisher = pubsub_v1.PublisherClient()
        self.bq_client = bigquery.Client()
        
        # Topic for BigQuery CDC events
        self.cdc_topic_path = self.publisher.topic_path(
            self.project_id, 
            "bq-cdc-events"
        )
        
    async def publish_row_change(self, 
                                table_name: str,
                                operation: str, 
                                row_data: Dict[str, Any],
                                old_data: Optional[Dict[str, Any]] = None):
        """Publish a row-level change event to Pub/Sub"""
        
        change_event = {
            "table": table_name,
            "operation": operation,  # INSERT, UPDATE, DELETE
            "new_data": row_data,
            "old_data": old_data,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "bigquery"
        }
        
        # Add metadata for routing
        attributes = {
            "table": table_name,
            "operation": operation,
            "timestamp": change_event["timestamp"]
        }
        
        # Add entity-specific attributes if available
        if "entity_id" in row_data:
            attributes["entity_id"] = str(row_data["entity_id"])
        if "address" in row_data:
            attributes["address"] = str(row_data["address"])
            
        try:
            future = self.publisher.publish(
                self.cdc_topic_path,
                json.dumps(change_event).encode('utf-8'),
                **attributes
            )
            
            message_id = future.result()
            
            logger.info("Published BigQuery CDC event",
                       table=table_name,
                       operation=operation,
                       message_id=message_id)
                       
            return message_id
            
        except Exception as e:
            logger.error("Failed to publish CDC event",
                        table=table_name,
                        operation=operation,
                        error=str(e))
            raise
    
    async def setup_change_streams(self, tables: list):
        """Set up BigQuery change streams for specified tables"""
        
        for table_name in tables:
            # Create a change stream for the table
            change_stream_sql = f"""
            CREATE OR REPLACE CHANGE STREAM {table_name}_stream
            FOR TABLE `{self.project_id}.ethereum.{table_name}`
            OPTIONS (
                value_capture_type = 'NEW_ROW',
                retention_period = '7d'
            )
            """
            
            try:
                query_job = self.bq_client.query(change_stream_sql)
                query_job.result()  # Wait for completion
                
                logger.info("Created change stream", 
                           table=table_name,
                           stream=f"{table_name}_stream")
                           
            except Exception as e:
                logger.warning("Failed to create change stream",
                              table=table_name,
                              error=str(e))


# Global CDC publisher instance
cdc_publisher = BigQueryCDCPublisher()


async def publish_entity_change(entity_id: str, 
                               entity_type: str,
                               operation: str,
                               new_data: Dict[str, Any],
                               old_data: Optional[Dict[str, Any]] = None):
    """Convenience function to publish entity changes"""
    
    await cdc_publisher.publish_row_change(
        table_name="entities",
        operation=operation,
        row_data={
            "entity_id": entity_id,
            "entity_type": entity_type,
            **new_data
        },
        old_data=old_data
    )


async def publish_transaction_change(tx_hash: str,
                                   operation: str, 
                                   tx_data: Dict[str, Any]):
    """Convenience function to publish transaction changes"""
    
    await cdc_publisher.publish_row_change(
        table_name="transactions",
        operation=operation,
        row_data={
            "transaction_hash": tx_hash,
            **tx_data
        }
    )


# Initialize CDC streams for key tables
MONITORED_TABLES = [
    "entities",
    "transactions", 
    "addresses",
    "contracts",
    "labels"
]


async def initialize_cdc():
    """Initialize CDC monitoring for all tables"""
    await cdc_publisher.setup_change_streams(MONITORED_TABLES)
    logger.info("CDC initialization complete", tables=MONITORED_TABLES)
