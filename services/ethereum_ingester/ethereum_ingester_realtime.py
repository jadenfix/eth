#!/usr/bin/env python3
"""
Real-time Ethereum Ingestion Service
Connects to Alchemy/Infura and streams data to BigQuery
"""
import os
import time
import json
import asyncio
import websockets
import requests
from google.cloud import bigquery
from google.cloud import pubsub_v1
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EthereumIngester:
    def __init__(self):
        self.alchemy_key = os.getenv('ALCHEMY_API_KEY')
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.dataset_id = os.getenv('BIGQUERY_DATASET')
        self.table_id = os.getenv('BIGQUERY_TABLE_RAW')
        
        # Initialize clients
        self.bq_client = bigquery.Client(project=self.project_id)
        self.publisher = pubsub_v1.PublisherClient()
        
        # Pub/Sub topic (fallback to direct BigQuery if topic doesn't exist)
        self.topic_path = self.publisher.topic_path(self.project_id, 'raw-chain-events')
        
    def get_latest_block(self):
        """Fetch latest block from Alchemy"""
        url = f"https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_key}"
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBlockByNumber",
            "params": ["latest", True],
            "id": 1
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()['result']
        except Exception as e:
            logger.error(f"Error fetching block: {e}")
        return None
    
    def process_block(self, block_data):
        """Process block data and insert into BigQuery"""
        if not block_data:
            return
            
        # Extract transactions
        transactions = []
        for tx in block_data.get('transactions', [])[:10]:  # Limit for demo
            if isinstance(tx, dict):
                tx_data = {
                    'transaction_hash': tx.get('hash'),
                    'block_number': int(block_data.get('number', '0x0'), 16),
                    'block_hash': block_data.get('hash'),
                    'from_address': tx.get('from'),
                    'to_address': tx.get('to'),
                    'value': float(int(tx.get('value', '0x0'), 16)) / 1e18,  # Convert to ETH
                    'gas_used': int(tx.get('gas', '0x0'), 16),
                    'gas_price': int(tx.get('gasPrice', '0x0'), 16),
                    'timestamp': datetime.now().isoformat(),
                    'raw_data': json.dumps(tx)
                }
                transactions.append(tx_data)
        
        # Insert into BigQuery
        if transactions:
            try:
                table_ref = self.bq_client.dataset(self.dataset_id).table(self.table_id)
                errors = self.bq_client.insert_rows_json(table_ref, transactions)
                
                if not errors:
                    logger.info(f"✅ Inserted {len(transactions)} transactions from block {block_data.get('number')}")
                else:
                    logger.error(f"❌ BigQuery insert errors: {errors}")
                    
            except Exception as e:
                logger.error(f"❌ BigQuery error: {e}")
                
        # Try to publish to Pub/Sub (optional)
        try:
            for tx in transactions:
                message_data = json.dumps(tx).encode('utf-8')
                future = self.publisher.publish(self.topic_path, message_data)
                logger.debug(f"Published message: {future.result()}")
        except Exception as e:
            logger.debug(f"Pub/Sub not available (expected): {e}")
    
    def run(self):
        """Main ingestion loop"""
        logger.info("🚀 Starting Ethereum Ingester...")
        logger.info(f"Project: {self.project_id}")
        logger.info(f"Dataset: {self.dataset_id}")
        logger.info(f"Table: {self.table_id}")
        
        while True:
            try:
                # Fetch latest block
                block_data = self.get_latest_block()
                if block_data:
                    self.process_block(block_data)
                else:
                    logger.warning("No block data received")
                
                # Wait before next fetch
                time.sleep(10)  # 10 second intervals
                
            except KeyboardInterrupt:
                logger.info("🛑 Ingester stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    ingester = EthereumIngester()
    ingester.run()
