"""
Blockchain data ingestion service.

Pulls real-time data from Ethereum via Alchemy/Infura, normalizes to canonical 
chain-event format, and publishes to Pub/Sub for downstream processing.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone

import structlog
from web3 import Web3
from google.cloud import pubsub_v1
from google.cloud import bigquery
import aiohttp

# Configure structured logging
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


@dataclass
class ChainEvent:
    """Canonical blockchain event structure."""
    block_number: int
    transaction_hash: str
    log_index: Optional[int]
    contract_address: Optional[str]
    event_name: str
    event_data: Dict[str, Any]
    timestamp: datetime
    chain_id: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'block_number': self.block_number,
            'transaction_hash': self.transaction_hash,
            'log_index': self.log_index,
            'contract_address': self.contract_address,
            'event_name': self.event_name,
            'event_data': self.event_data,
            'timestamp': self.timestamp.isoformat(),
            'chain_id': self.chain_id,
            'ingestion_timestamp': datetime.now(timezone.utc).isoformat()
        }


class EthereumIngester:
    """Ethereum blockchain data ingester."""
    
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(
            f"https://eth-mainnet.alchemyapi.io/v2/{os.getenv('ALCHEMY_API_KEY')}"
        ))
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            os.getenv('GOOGLE_CLOUD_PROJECT'),
            'raw-chain-events'
        )
        self.logger = logger.bind(service="ethereum-ingester")
        
    async def start_streaming(self):
        """Start streaming blockchain events."""
        self.logger.info("Starting Ethereum event streaming")
        
        # Subscribe to new blocks
        latest_block = self.web3.eth.block_number
        self.logger.info("Starting from block", block_number=latest_block)
        
        while True:
            try:
                current_block = self.web3.eth.block_number
                
                # Process any new blocks
                if current_block > latest_block:
                    for block_num in range(latest_block + 1, current_block + 1):
                        await self._process_block(block_num)
                    latest_block = current_block
                    
                await asyncio.sleep(1)  # Check for new blocks every second
                
            except Exception as e:
                self.logger.error("Error in streaming loop", error=str(e))
                await asyncio.sleep(5)  # Backoff on error
                
    async def _process_block(self, block_number: int):
        """Process a single block and extract events."""
        try:
            block = self.web3.eth.get_block(block_number, full_transactions=True)
            self.logger.info("Processing block", block_number=block_number, 
                           tx_count=len(block.transactions))
            
            # Process each transaction
            for tx in block.transactions:
                await self._process_transaction(tx, block)
                
        except Exception as e:
            self.logger.error("Error processing block", 
                            block_number=block_number, error=str(e))
    
    async def _process_transaction(self, tx, block):
        """Process a transaction and extract events."""
        try:
            # Get transaction receipt for events
            receipt = self.web3.eth.get_transaction_receipt(tx.hash)
            
            # Create base transaction event
            tx_event = ChainEvent(
                block_number=block.number,
                transaction_hash=tx.hash.hex(),
                log_index=None,
                contract_address=tx.to,
                event_name="TRANSACTION",
                event_data={
                    'from': tx['from'],
                    'to': tx.to,
                    'value': str(tx.value),
                    'gas_used': receipt.gasUsed,
                    'gas_price': str(tx.gasPrice),
                    'status': receipt.status
                },
                timestamp=datetime.fromtimestamp(block.timestamp, tz=timezone.utc),
                chain_id=1  # Ethereum mainnet
            )
            
            await self._publish_event(tx_event)
            
            # Process contract logs (events)
            for log_index, log in enumerate(receipt.logs):
                await self._process_log(log, log_index, block, tx.hash.hex())
                
        except Exception as e:
            self.logger.error("Error processing transaction", 
                            tx_hash=tx.hash.hex(), error=str(e))
    
    async def _process_log(self, log, log_index: int, block, tx_hash: str):
        """Process a contract event log."""
        try:
            # Basic event parsing - can be enhanced with ABI decoding
            event = ChainEvent(
                block_number=block.number,
                transaction_hash=tx_hash,
                log_index=log_index,
                contract_address=log.address,
                event_name="CONTRACT_EVENT",
                event_data={
                    'topics': [topic.hex() for topic in log.topics],
                    'data': log.data,
                    'removed': log.removed
                },
                timestamp=datetime.fromtimestamp(block.timestamp, tz=timezone.utc),
                chain_id=1
            )
            
            await self._publish_event(event)
            
        except Exception as e:
            self.logger.error("Error processing log", 
                            log_index=log_index, error=str(e))
    
    async def _publish_event(self, event: ChainEvent):
        """Publish event to Pub/Sub."""
        try:
            message_data = json.dumps(event.to_dict()).encode('utf-8')
            
            # Add attributes for filtering
            attributes = {
                'event_name': event.event_name,
                'chain_id': str(event.chain_id),
                'block_number': str(event.block_number)
            }
            
            if event.contract_address:
                attributes['contract_address'] = event.contract_address
            
            future = self.publisher.publish(
                self.topic_path, 
                message_data, 
                **attributes
            )
            
            # Don't wait for publish to complete - fire and forget for performance
            self.logger.debug("Published event", event_name=event.event_name,
                            block_number=event.block_number)
            
        except Exception as e:
            self.logger.error("Error publishing event", error=str(e))


async def main():
    """Main ingestion loop."""
    ingester = EthereumIngester()
    await ingester.start_streaming()


if __name__ == "__main__":
    asyncio.run(main())
