import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class WhaleMovement:
    whale_id: str
    address: str
    movement_type: str  # 'LARGE_TRANSFER', 'ACCUMULATION', 'DISTRIBUTION', 'EXCHANGE_DEPOSIT'
    value_eth: float
    value_usd: float
    timestamp: datetime
    from_address: Optional[str]
    to_address: Optional[str]
    transaction_hash: str
    confidence_score: float
    metadata: Dict[str, Any]

class WhaleTracker:
    def __init__(self):
        self.whale_thresholds = {
            'large_transfer': 100,  # ETH
            'whale_balance': 1000,  # ETH
            'accumulation_threshold': 50,  # ETH
            'distribution_threshold': 50,  # ETH
        }
        
        self.known_whales = set()
        self.whale_movements = []
        self.exchange_addresses = {
            '0x21a31ee1afc51d94c2efccaa2092ad1028285549',  # Binance
            '0xdfd5293d8e347dfe59e90efd55b2956a1343963d',  # Binance
            '0x28c6c06298d514db089934071355e5743bf21d60',  # Binance
            '0x21a31ee1afc51d94c2efccaa2092ad1028285549',  # Coinbase
            '0xa090e606e30bd747d4e6245a1517ebe430f0057e',  # Coinbase
        }
    
    async def track_whale_movements(self, transactions: List[Dict[str, Any]]) -> List[WhaleMovement]:
        """Track whale movements in transactions"""
        movements = []
        
        for tx in transactions:
            value_eth = tx.get('value', 0) / 1e18
            
            # Check for large transfers
            if value_eth > self.whale_thresholds['large_transfer']:
                movement = await self._analyze_large_transfer(tx)
                if movement:
                    movements.append(movement)
            
            # Check for whale balance changes
            await self._update_whale_balances(tx)
        
        # Analyze accumulation/distribution patterns
        accumulation_movements = await self._detect_accumulation_patterns(transactions)
        movements.extend(accumulation_movements)
        
        distribution_movements = await self._detect_distribution_patterns(transactions)
        movements.extend(distribution_movements)
        
        return movements
    
    async def _analyze_large_transfer(self, tx: Dict[str, Any]) -> Optional[WhaleMovement]:
        """Analyze a large transfer transaction"""
        value_eth = tx.get('value', 0) / 1e18
        from_addr = tx.get('from', '')
        to_addr = tx.get('to', '')
        
        # Determine movement type
        movement_type = 'LARGE_TRANSFER'
        
        if to_addr.lower() in self.exchange_addresses:
            movement_type = 'EXCHANGE_DEPOSIT'
        elif from_addr.lower() in self.exchange_addresses:
            movement_type = 'EXCHANGE_WITHDRAWAL'
        
        # Calculate confidence based on amount and addresses
        confidence = min(value_eth / 1000, 1.0)  # Higher confidence for larger amounts
        
        # Estimate USD value (simplified)
        value_usd = value_eth * 2000  # Assume $2000 per ETH
        
        return WhaleMovement(
            whale_id=f"whale_{from_addr}_{datetime.now().timestamp()}",
            address=from_addr,
            movement_type=movement_type,
            value_eth=value_eth,
            value_usd=value_usd,
            timestamp=datetime.now(),
            from_address=from_addr,
            to_address=to_addr,
            transaction_hash=tx.get('hash', ''),
            confidence_score=confidence,
            metadata={
                'gas_price': tx.get('gasPrice', 0),
                'gas_used': tx.get('gasUsed', 0),
                'block_number': tx.get('blockNumber', 0)
            }
        )
    
    async def _update_whale_balances(self, tx: Dict[str, Any]):
        """Update whale balance tracking"""
        value_eth = tx.get('value', 0) / 1e18
        from_addr = tx.get('from', '')
        to_addr = tx.get('to', '')
        
        # Track addresses with large balances
        if value_eth > self.whale_thresholds['whale_balance']:
            self.known_whales.add(from_addr)
            self.known_whales.add(to_addr)
    
    async def _detect_accumulation_patterns(self, transactions: List[Dict[str, Any]]) -> List[WhaleMovement]:
        """Detect accumulation patterns (buying)"""
        movements = []
        
        # Group transactions by address
        address_transactions = defaultdict(list)
        for tx in transactions:
            to_addr = tx.get('to', '')
            if to_addr:
                address_transactions[to_addr].append(tx)
        
        # Check for accumulation patterns
        for address, txs in address_transactions.items():
            if len(txs) >= 3:  # Multiple transactions
                total_value = sum(tx.get('value', 0) / 1e18 for tx in txs)
                
                if total_value > self.whale_thresholds['accumulation_threshold']:
                    # Check if from exchange (buying)
                    from_exchange = any(
                        tx.get('from', '').lower() in self.exchange_addresses 
                        for tx in txs
                    )
                    
                    if from_exchange:
                        movement = WhaleMovement(
                            whale_id=f"accumulation_{address}_{datetime.now().timestamp()}",
                            address=address,
                            movement_type='ACCUMULATION',
                            value_eth=total_value,
                            value_usd=total_value * 2000,
                            timestamp=datetime.now(),
                            from_address=None,
                            to_address=address,
                            transaction_hash=','.join(tx.get('hash', '') for tx in txs),
                            confidence_score=0.8,
                            metadata={
                                'transaction_count': len(txs),
                                'avg_value': total_value / len(txs),
                                'pattern': 'multiple_buys'
                            }
                        )
                        movements.append(movement)
        
        return movements
    
    async def _detect_distribution_patterns(self, transactions: List[Dict[str, Any]]) -> List[WhaleMovement]:
        """Detect distribution patterns (selling)"""
        movements = []
        
        # Group transactions by address
        address_transactions = defaultdict(list)
        for tx in transactions:
            from_addr = tx.get('from', '')
            if from_addr:
                address_transactions[from_addr].append(tx)
        
        # Check for distribution patterns
        for address, txs in address_transactions.items():
            if len(txs) >= 3:  # Multiple transactions
                total_value = sum(tx.get('value', 0) / 1e18 for tx in txs)
                
                if total_value > self.whale_thresholds['distribution_threshold']:
                    # Check if to exchange (selling)
                    to_exchange = any(
                        tx.get('to', '').lower() in self.exchange_addresses 
                        for tx in txs
                    )
                    
                    if to_exchange:
                        movement = WhaleMovement(
                            whale_id=f"distribution_{address}_{datetime.now().timestamp()}",
                            address=address,
                            movement_type='DISTRIBUTION',
                            value_eth=total_value,
                            value_usd=total_value * 2000,
                            timestamp=datetime.now(),
                            from_address=address,
                            to_address=None,
                            transaction_hash=','.join(tx.get('hash', '') for tx in txs),
                            confidence_score=0.8,
                            metadata={
                                'transaction_count': len(txs),
                                'avg_value': total_value / len(txs),
                                'pattern': 'multiple_sells'
                            }
                        )
                        movements.append(movement)
        
        return movements
    
    async def get_whale_statistics(self) -> Dict[str, Any]:
        """Get whale movement statistics"""
        return {
            'known_whales': len(self.known_whales),
            'total_movements': len(self.whale_movements),
            'movements_by_type': self._count_movements_by_type(),
            'largest_movement': self._get_largest_movement(),
            'recent_activity': self._get_recent_activity()
        }
    
    def _count_movements_by_type(self) -> Dict[str, int]:
        """Count movements by type"""
        counts = defaultdict(int)
        for movement in self.whale_movements:
            counts[movement.movement_type] += 1
        return dict(counts)
    
    def _get_largest_movement(self) -> Optional[Dict[str, Any]]:
        """Get the largest whale movement"""
        if not self.whale_movements:
            return None
        
        largest = max(self.whale_movements, key=lambda m: m.value_eth)
        return {
            'address': largest.address,
            'value_eth': largest.value_eth,
            'value_usd': largest.value_usd,
            'movement_type': largest.movement_type,
            'timestamp': largest.timestamp.isoformat()
        }
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent whale activity"""
        recent = [
            m for m in self.whale_movements 
            if m.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        return [
            {
                'address': m.address,
                'value_eth': m.value_eth,
                'movement_type': m.movement_type,
                'timestamp': m.timestamp.isoformat()
            }
            for m in recent[:10]  # Last 10 movements
        ]
    
    async def process_sample_transactions(self, transactions: List[Dict[str, Any]]) -> List[WhaleMovement]:
        """Process sample transactions for whale tracking"""
        return await self.track_whale_movements(transactions) 