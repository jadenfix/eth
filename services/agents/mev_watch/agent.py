"""
MEV Watch Agent - Detects Maximum Extractable Value opportunities and attacks.

Monitors mempool for MEV activities including:
- Sandwich attacks
- Front-running 
- Back-running
- Arbitrage opportunities
- Liquidation bots
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib

import structlog
from google.cloud import pubsub_v1
from google.cloud import bigquery
from web3 import Web3

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
class MEVSignal:
    """MEV detection signal."""
    signal_id: str
    agent_name: str = "mev_watch"
    signal_type: str = ""
    confidence_score: float = 0.0
    related_addresses: List[str] = None
    related_transactions: List[str] = None
    description: str = ""
    severity: str = "LOW"
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.related_addresses is None:
            self.related_addresses = []
        if self.related_transactions is None:
            self.related_transactions = []
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'signal_id': self.signal_id,
            'agent_name': self.agent_name,
            'signal_type': self.signal_type,
            'confidence_score': self.confidence_score,
            'related_addresses': self.related_addresses,
            'related_transactions': self.related_transactions,
            'description': self.description,
            'severity': self.severity,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class MEVWatchAgent:
    """MEV detection and monitoring agent."""
    
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(
            f"https://eth-mainnet.alchemyapi.io/v2/{os.getenv('ALCHEMY_API_KEY')}"
        ))
        
        # Pub/Sub setup
        self.subscriber = pubsub_v1.SubscriberClient()
        self.publisher = pubsub_v1.PublisherClient()
        
        self.subscription_path = self.subscriber.subscription_path(
            os.getenv('GOOGLE_CLOUD_PROJECT'),
            'agents-raw-events-sub'
        )
        
        self.signals_topic = self.publisher.topic_path(
            os.getenv('GOOGLE_CLOUD_PROJECT'),
            'ai-signals'
        )
        
        self.logger = logger.bind(service="mev-watch-agent")
        
        # MEV detection state
        self.recent_transactions: Dict[str, Dict] = {}  # Block -> tx list
        self.known_mev_bots: Set[str] = set()
        self.dex_contracts = {
            '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',  # Uniswap V2 Router
            '0xE592427A0AEce92De3Edee1F18E0157C05861564',  # Uniswap V3 Router
            '0x1111111254EEB25477B68fb85Ed929f73A960582',  # 1inch Router
        }
        
    async def start_monitoring(self):
        """Start MEV monitoring."""
        self.logger.info("Starting MEV watch agent")
        
        # Start Pub/Sub subscriber
        flow_control = pubsub_v1.types.FlowControl(max_messages=100)
        
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self._process_event,
            flow_control=flow_control
        )
        
        self.logger.info("Listening for blockchain events...")
        
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
            self.logger.info("MEV watch agent stopped")
    
    def _process_event(self, message):
        """Process incoming blockchain event."""
        try:
            event_data = json.loads(message.data.decode('utf-8'))
            
            # Only process transaction events for MEV detection
            if event_data.get('event_name') == 'TRANSACTION':
                asyncio.create_task(self._analyze_transaction(event_data))
            
            message.ack()
            
        except Exception as e:
            self.logger.error("Error processing event", error=str(e))
            message.nack()
    
    async def _analyze_transaction(self, tx_data: Dict[str, Any]):
        """Analyze transaction for MEV patterns."""
        try:
            block_number = tx_data['block_number']
            tx_hash = tx_data['transaction_hash']
            
            # Store transaction for block-level analysis
            if block_number not in self.recent_transactions:
                self.recent_transactions[block_number] = []
            
            self.recent_transactions[block_number].append(tx_data)
            
            # Clean old blocks (keep last 10 blocks)
            blocks_to_remove = [b for b in self.recent_transactions.keys() 
                               if b < block_number - 10]
            for block in blocks_to_remove:
                del self.recent_transactions[block]
            
            # Run MEV detection algorithms
            await self._detect_sandwich_attack(tx_data, block_number)
            await self._detect_frontrunning(tx_data, block_number)
            await self._detect_arbitrage(tx_data)
            await self._detect_mev_bot(tx_data)
            
        except Exception as e:
            self.logger.error("Error analyzing transaction", 
                            tx_hash=tx_data.get('transaction_hash'), error=str(e))
    
    async def _detect_sandwich_attack(self, tx_data: Dict[str, Any], block_number: int):
        """Detect sandwich attacks in the same block."""
        try:
            tx_hash = tx_data['transaction_hash']
            from_addr = tx_data['event_data'].get('from')
            to_addr = tx_data['event_data'].get('to')
            
            # Check if this is a DEX interaction
            if to_addr not in self.dex_contracts:
                return
            
            # Look for sandwich pattern in same block
            block_txs = self.recent_transactions.get(block_number, [])
            
            # Find transactions from same address before and after
            same_address_txs = [tx for tx in block_txs 
                               if tx['event_data'].get('from') == from_addr 
                               and tx['transaction_hash'] != tx_hash]
            
            if len(same_address_txs) >= 2:
                # Potential sandwich - calculate confidence
                confidence = min(0.8, 0.3 + (len(same_address_txs) * 0.1))
                
                signal = MEVSignal(
                    signal_id=self._generate_signal_id(tx_hash, "sandwich"),
                    signal_type="SANDWICH_ATTACK",
                    confidence_score=confidence,
                    related_addresses=[from_addr, to_addr],
                    related_transactions=[tx_hash] + [tx['transaction_hash'] for tx in same_address_txs],
                    description=f"Potential sandwich attack detected in block {block_number}",
                    severity="MEDIUM" if confidence > 0.6 else "LOW",
                    metadata={
                        'block_number': block_number,
                        'dex_contract': to_addr,
                        'transaction_count': len(same_address_txs) + 1,
                        'pattern': 'sandwich'
                    }
                )
                
                await self._publish_signal(signal)
                
        except Exception as e:
            self.logger.error("Error in sandwich detection", error=str(e))
    
    async def _detect_frontrunning(self, tx_data: Dict[str, Any], block_number: int):
        """Detect front-running patterns."""
        try:
            tx_hash = tx_data['transaction_hash']
            gas_price = int(tx_data['event_data'].get('gas_price', '0'))
            to_addr = tx_data['event_data'].get('to')
            
            if to_addr not in self.dex_contracts:
                return
            
            # Check for unusually high gas price (potential front-running)
            if gas_price > 100_000_000_000:  # > 100 gwei
                
                # Look for similar transactions in previous blocks with lower gas
                prev_blocks = [b for b in self.recent_transactions.keys() 
                              if b < block_number and b > block_number - 3]
                
                similar_txs = []
                for prev_block in prev_blocks:
                    for prev_tx in self.recent_transactions[prev_block]:
                        if (prev_tx['event_data'].get('to') == to_addr and
                            int(prev_tx['event_data'].get('gas_price', '0')) < gas_price * 0.5):
                            similar_txs.append(prev_tx)
                
                if similar_txs:
                    confidence = min(0.9, 0.5 + (gas_price / 200_000_000_000))
                    
                    signal = MEVSignal(
                        signal_id=self._generate_signal_id(tx_hash, "frontrun"),
                        signal_type="FRONTRUNNING",
                        confidence_score=confidence,
                        related_addresses=[tx_data['event_data'].get('from'), to_addr],
                        related_transactions=[tx_hash] + [tx['transaction_hash'] for tx in similar_txs[:3]],
                        description=f"Potential front-running detected with {gas_price/1e9:.1f} gwei gas price",
                        severity="HIGH" if confidence > 0.7 else "MEDIUM",
                        metadata={
                            'gas_price_gwei': gas_price / 1e9,
                            'block_number': block_number,
                            'similar_tx_count': len(similar_txs)
                        }
                    )
                    
                    await self._publish_signal(signal)
                    
        except Exception as e:
            self.logger.error("Error in frontrunning detection", error=str(e))
    
    async def _detect_arbitrage(self, tx_data: Dict[str, Any]):
        """Detect arbitrage opportunities."""
        try:
            tx_hash = tx_data['transaction_hash']
            from_addr = tx_data['event_data'].get('from')
            to_addr = tx_data['event_data'].get('to')
            value = int(tx_data['event_data'].get('value', '0'))
            
            # Look for high-value transactions to DEX contracts
            if to_addr in self.dex_contracts and value > 10**18:  # > 1 ETH
                
                # Check if this address has made multiple DEX transactions recently
                recent_dex_txs = []
                for block_txs in self.recent_transactions.values():
                    for tx in block_txs:
                        if (tx['event_data'].get('from') == from_addr and 
                            tx['event_data'].get('to') in self.dex_contracts and
                            tx['transaction_hash'] != tx_hash):
                            recent_dex_txs.append(tx)
                
                if len(recent_dex_txs) >= 2:
                    confidence = min(0.85, 0.4 + (len(recent_dex_txs) * 0.1))
                    
                    signal = MEVSignal(
                        signal_id=self._generate_signal_id(tx_hash, "arbitrage"),
                        signal_type="ARBITRAGE",
                        confidence_score=confidence,
                        related_addresses=[from_addr],
                        related_transactions=[tx_hash] + [tx['transaction_hash'] for tx in recent_dex_txs[:5]],
                        description=f"Potential arbitrage activity detected with {value/1e18:.2f} ETH volume",
                        severity="LOW",
                        metadata={
                            'value_eth': value / 1e18,
                            'dex_transaction_count': len(recent_dex_txs) + 1,
                            'dex_contracts': list(set([tx['event_data'].get('to') for tx in recent_dex_txs + [tx_data]]))
                        }
                    )
                    
                    await self._publish_signal(signal)
                    
        except Exception as e:
            self.logger.error("Error in arbitrage detection", error=str(e))
    
    async def _detect_mev_bot(self, tx_data: Dict[str, Any]):
        """Detect known MEV bot behavior patterns."""
        try:
            from_addr = tx_data['event_data'].get('from')
            gas_price = int(tx_data['event_data'].get('gas_price', '0'))
            
            # Check for bot-like behavior: consistent high gas, frequent DEX interactions
            recent_tx_count = sum(
                len([tx for tx in block_txs if tx['event_data'].get('from') == from_addr])
                for block_txs in self.recent_transactions.values()
            )
            
            if recent_tx_count >= 5 and gas_price > 50_000_000_000:  # > 50 gwei
                
                if from_addr not in self.known_mev_bots:
                    self.known_mev_bots.add(from_addr)
                    
                    signal = MEVSignal(
                        signal_id=self._generate_signal_id(from_addr, "mev_bot"),
                        signal_type="MEV_BOT",
                        confidence_score=0.7,
                        related_addresses=[from_addr],
                        related_transactions=[tx_data['transaction_hash']],
                        description=f"MEV bot identified: {from_addr}",
                        severity="MEDIUM",
                        metadata={
                            'transaction_frequency': recent_tx_count,
                            'average_gas_price_gwei': gas_price / 1e9,
                            'bot_type': 'suspected_mev'
                        }
                    )
                    
                    await self._publish_signal(signal)
                    
        except Exception as e:
            self.logger.error("Error in MEV bot detection", error=str(e))
    
    def _generate_signal_id(self, identifier: str, signal_type: str) -> str:
        """Generate unique signal ID."""
        return hashlib.md5(f"{identifier}-{signal_type}-{datetime.now().isoformat()}".encode()).hexdigest()
    
    async def _publish_signal(self, signal: MEVSignal):
        """Publish MEV signal to Pub/Sub."""
        try:
            message_data = json.dumps(signal.to_dict()).encode('utf-8')
            
            attributes = {
                'agent_name': signal.agent_name,
                'signal_type': signal.signal_type,
                'severity': signal.severity
            }
            
            future = self.publisher.publish(
                self.signals_topic,
                message_data,
                **attributes
            )
            
            self.logger.info("Published MEV signal", 
                           signal_type=signal.signal_type,
                           confidence=signal.confidence_score,
                           severity=signal.severity)
            
        except Exception as e:
            self.logger.error("Error publishing signal", error=str(e))


async def main():
    """Main agent loop."""
    agent = MEVWatchAgent()
    await agent.start_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
