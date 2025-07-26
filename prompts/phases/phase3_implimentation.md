# Phase 3: Intelligence Agents Implementation Guide



MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 

MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 

## �� **PHASE 3 OVERVIEW**

**Goal:** Implement the core compliance and risk detection features with intelligent agents

**Duration:** 2 Weeks (Week 5: MEV & Risk Detection, Week 6: Sanctions & Compliance)

**Prerequisites:** ✅ Phase 1 completed (Authentication, Multi-chain data), ✅ Phase 2 completed (Entity resolution, Graph database)
**Target Status:** 🤖 MEV detection + Risk scoring + Sanctions screening + Anomaly detection

---

## 📋 **WEEK 5: MEV & RISK DETECTION**

### **Day 1-2: MEV Detection Algorithms**

#### **Step 1: Create MEV Detection Service**
**File:** `services/mev_agent/mev_detector.py`

```python
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict, deque

@dataclass
class MEVSignal:
    signal_id: str
    signal_type: str  # 'SANDWICH_ATTACK', 'FRONT_RUNNING', 'BACK_RUNNING', 'LIQUIDATION'
    confidence_score: float
    block_number: int
    timestamp: datetime
    target_transaction: Dict[str, Any]
    mev_transactions: List[Dict[str, Any]]
    profit_estimate: float
    gas_used: int
    addresses_involved: List[str]
    metadata: Dict[str, Any]

class MEVDetector:
    def __init__(self):
        self.recent_blocks = deque(maxlen=100)  # Keep last 100 blocks
        self.sandwich_patterns = defaultdict(list)
        self.liquidation_thresholds = {
            'aave': 0.8,  # 80% health factor
            'compound': 1.1,  # 110% collateral ratio
            'maker': 1.5  # 150% collateralization ratio
        }
        
    async def detect_sandwich_attack(self, block_transactions: List[Dict[str, Any]]) -> List[MEVSignal]:
        """Detect sandwich attacks in a block"""
        signals = []
        
        # Group transactions by target (victim transaction)
        potential_victims = []
        mev_candidates = []
        
        for tx in block_transactions:
            # Identify potential victim transactions (normal gas prices)
            if self._is_potential_victim(tx):
                potential_victims.append(tx)
            
            # Identify MEV transactions (high gas prices, specific patterns)
            if self._is_mev_candidate(tx):
                mev_candidates.append(tx)
        
        # Check for sandwich patterns
        for victim in potential_victims:
            sandwich = self._find_sandwich_pattern(victim, mev_candidates)
            if sandwich:
                signal = self._create_sandwich_signal(victim, sandwich)
                signals.append(signal)
        
        return signals
    
    def _is_potential_victim(self, tx: Dict[str, Any]) -> bool:
        """Identify potential victim transactions"""
        gas_price = tx.get('gasPrice', 0) / 1e9  # Convert to gwei
        
        # Normal gas prices (not MEV)
        if gas_price < 50:  # Less than 50 gwei
            return True
        
        # Check for DEX interactions (common victims)
        to_address = tx.get('to', '').lower()
        dex_addresses = {
            '0x7a250d5630b4cf539739df2c5dacb4c659f2488d',  # Uniswap V2
            '0xe592427a0aece92de3edee1f18e0157c05861564',  # Uniswap V3
            '0x1111111254fb6c44bac0bed2854e76f90643097d',  # 1inch
        }
        
        if to_address in dex_addresses:
            return True
        
        return False
    
    def _is_mev_candidate(self, tx: Dict[str, Any]) -> bool:
        """Identify potential MEV transactions"""
        gas_price = tx.get('gasPrice', 0) / 1e9
        
        # High gas prices
        if gas_price > 200:  # More than 200 gwei
            return True
        
        # Check for known MEV bot patterns
        from_address = tx.get('from', '').lower()
        known_mev_bots = {
            '0x0000000000000000000000000000000000000000',  # Flashbots
            '0xdaFCE5670d3F67da9A3A44D6f3e82C7b8c5c3b3b',  # Example MEV bot
        }
        
        if from_address in known_mev_bots:
            return True
        
        # Check for flash loan patterns
        if self._has_flash_loan_pattern(tx):
            return True
        
        return False
    
    def _has_flash_loan_pattern(self, tx: Dict[str, Any]) -> bool:
        """Detect flash loan patterns in transaction"""
        input_data = tx.get('input', '')
        
        # Flash loan function signatures
        flash_loan_signatures = [
            '0x5cffe9de',  # Aave flash loan
            '0xb2a02ff1',  # Compound flash loan
            '0x1cff79cd',  # dYdX flash loan
        ]
        
        for signature in flash_loan_signatures:
            if input_data.startswith(signature):
                return True
        
        return False
    
    def _find_sandwich_pattern(self, victim: Dict[str, Any], mev_candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find sandwich attack pattern around victim transaction"""
        victim_gas_price = victim.get('gasPrice', 0)
        victim_position = self._get_transaction_position(victim)
        
        front_run = None
        back_run = None
        
        for mev_tx in mev_candidates:
            mev_gas_price = mev_tx.get('gasPrice', 0)
            mev_position = self._get_transaction_position(mev_tx)
            
            # Front run: higher gas price, earlier position
            if (mev_gas_price > victim_gas_price * 1.5 and 
                mev_position < victim_position):
                front_run = mev_tx
            
            # Back run: higher gas price, later position
            elif (mev_gas_price > victim_gas_price * 1.5 and 
                  mev_position > victim_position):
                back_run = mev_tx
        
        if front_run and back_run:
            return {
                'front_run': front_run,
                'victim': victim,
                'back_run': back_run
            }
        
        return None
    
    def _get_transaction_position(self, tx: Dict[str, Any]) -> int:
        """Get transaction position in block (simplified)"""
        # In a real implementation, this would use the actual transaction index
        return tx.get('transactionIndex', 0)
    
    def _create_sandwich_signal(self, victim: Dict[str, Any], sandwich: Dict[str, Any]) -> MEVSignal:
        """Create MEV signal for sandwich attack"""
        front_run = sandwich['front_run']
        back_run = sandwich['back_run']
        
        # Calculate profit estimate
        profit = self._estimate_sandwich_profit(victim, front_run, back_run)
        
        # Calculate confidence based on gas price differences
        confidence = min(
            (front_run['gasPrice'] / victim['gasPrice']) * 
            (back_run['gasPrice'] / victim['gasPrice']) / 10, 
            1.0
        )
        
        return MEVSignal(
            signal_id=f"sandwich_{victim['hash']}_{datetime.now().timestamp()}",
            signal_type='SANDWICH_ATTACK',
            confidence_score=confidence,
            block_number=victim.get('blockNumber', 0),
            timestamp=datetime.now(),
            target_transaction=victim,
            mev_transactions=[front_run, back_run],
            profit_estimate=profit,
            gas_used=front_run.get('gasUsed', 0) + back_run.get('gasUsed', 0),
            addresses_involved=[
                front_run.get('from', ''),
                victim.get('from', ''),
                back_run.get('from', '')
            ],
            metadata={
                'victim_gas_price': victim.get('gasPrice', 0),
                'front_run_gas_price': front_run.get('gasPrice', 0),
                'back_run_gas_price': back_run.get('gasPrice', 0),
                'gas_price_multiplier': front_run.get('gasPrice', 0) / victim.get('gasPrice', 1)
            }
        )
    
    def _estimate_sandwich_profit(self, victim: Dict[str, Any], front_run: Dict[str, Any], back_run: Dict[str, Any]) -> float:
        """Estimate profit from sandwich attack"""
        # Simplified profit estimation
        # In reality, this would analyze token transfers and price impact
        
        victim_value = victim.get('value', 0) / 1e18  # Convert from wei to ETH
        gas_cost = (front_run.get('gasUsed', 0) + back_run.get('gasUsed', 0)) * front_run.get('gasPrice', 0) / 1e18
        
        # Estimate profit as 0.1% of victim transaction value minus gas costs
        estimated_profit = victim_value * 0.001 - gas_cost
        
        return max(estimated_profit, 0)
    
    async def detect_liquidation_opportunities(self, block_transactions: List[Dict[str, Any]]) -> List[MEVSignal]:
        """Detect liquidation opportunities"""
        signals = []
        
        for tx in block_transactions:
            if self._is_liquidation_transaction(tx):
                signal = self._create_liquidation_signal(tx)
                signals.append(signal)
        
        return signals
    
    def _is_liquidation_transaction(self, tx: Dict[str, Any]) -> bool:
        """Identify liquidation transactions"""
        to_address = tx.get('to', '').lower()
        
        # Known liquidation contract addresses
        liquidation_contracts = {
            '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',  # Aave LendingPool
            '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B',  # Compound Comptroller
            '0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B',  # Maker Vault
        }
        
        if to_address in liquidation_contracts:
            return True
        
        # Check for liquidation function calls
        input_data = tx.get('input', '')
        liquidation_signatures = [
            '0x2986c0e5',  # Aave liquidation
            '0xef693bed',  # Compound liquidation
        ]
        
        for signature in liquidation_signatures:
            if input_data.startswith(signature):
                return True
        
        return False
    
    def _create_liquidation_signal(self, tx: Dict[str, Any]) -> MEVSignal:
        """Create MEV signal for liquidation"""
        return MEVSignal(
            signal_id=f"liquidation_{tx['hash']}_{datetime.now().timestamp()}",
            signal_type='LIQUIDATION',
            confidence_score=0.9,
            block_number=tx.get('blockNumber', 0),
            timestamp=datetime.now(),
            target_transaction=tx,
            mev_transactions=[tx],
            profit_estimate=0.1,  # Estimated liquidation profit
            gas_used=tx.get('gasUsed', 0),
            addresses_involved=[tx.get('from', ''), tx.get('to', '')],
            metadata={
                'liquidation_type': 'debt_liquidation',
                'protocol': self._identify_protocol(tx.get('to', '')),
                'gas_price': tx.get('gasPrice', 0)
            }
        )
    
    def _identify_protocol(self, contract_address: str) -> str:
        """Identify the protocol from contract address"""
        protocol_addresses = {
            '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9': 'aave',
            '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B': 'compound',
            '0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B': 'maker',
        }
        
        return protocol_addresses.get(contract_address.lower(), 'unknown')
```

#### **Step 2: Create MEV Agent Service**
**File:** `services/mev_agent/mev_agent.py`

```python
import asyncio
import json
from typing import Dict, List, Any
from datetime import datetime
from .mev_detector import MEVDetector, MEVSignal
from ..graph_api.neo4j_client import Neo4jClient
from ..access_control.audit_sink import AuditLogger

class MEVAgent:
    def __init__(self):
        self.detector = MEVDetector()
        self.neo4j_client = Neo4jClient()
        self.audit_logger = AuditLogger()
        self.signal_queue = asyncio.Queue()
        self.is_running = False
    
    async def start_monitoring(self):
        """Start MEV monitoring"""
        self.is_running = True
        
        # Start signal processing
        asyncio.create_task(self._process_signals())
        
        # Start block monitoring
        asyncio.create_task(self._monitor_blocks())
        
        print("MEV Agent started monitoring...")
    
    async def stop_monitoring(self):
        """Stop MEV monitoring"""
        self.is_running = False
        print("MEV Agent stopped monitoring...")
    
    async def _monitor_blocks(self):
        """Monitor new blocks for MEV activity"""
        while self.is_running:
            try:
                # Get latest block (in real implementation, this would be from blockchain)
                latest_block = await self._get_latest_block()
                
                if latest_block:
                    # Detect MEV in the block
                    signals = await self._analyze_block(latest_block)
                    
                    # Queue signals for processing
                    for signal in signals:
                        await self.signal_queue.put(signal)
                
                # Wait for next block
                await asyncio.sleep(12)  # Ethereum block time
                
            except Exception as e:
                print(f"Error monitoring blocks: {e}")
                await asyncio.sleep(5)
    
    async def _analyze_block(self, block_data: Dict[str, Any]) -> List[MEVSignal]:
        """Analyze a block for MEV activity"""
        transactions = block_data.get('transactions', [])
        
        signals = []
        
        # Detect sandwich attacks
        sandwich_signals = await self.detector.detect_sandwich_attack(transactions)
        signals.extend(sandwich_signals)
        
        # Detect liquidations
        liquidation_signals = await self.detector.detect_liquidation_opportunities(transactions)
        signals.extend(liquidation_signals)
        
        return signals
    
    async def _process_signals(self):
        """Process MEV signals"""
        while self.is_running:
            try:
                # Get signal from queue
                signal = await asyncio.wait_for(self.signal_queue.get(), timeout=1.0)
                
                # Process the signal
                await self._handle_signal(signal)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing signal: {e}")
    
    async def _handle_signal(self, signal: MEVSignal):
        """Handle a MEV signal"""
        try:
            # Log the signal
            await self._log_signal(signal)
            
            # Store in Neo4j
            await self._store_signal_in_graph(signal)
            
            # Send alert if confidence is high
            if signal.confidence_score > 0.7:
                await self._send_alert(signal)
            
            # Update risk scores
            await self._update_risk_scores(signal)
            
        except Exception as e:
            print(f"Error handling signal: {e}")
    
    async def _log_signal(self, signal: MEVSignal):
        """Log MEV signal to audit system"""
        audit_entry = {
            'signal_id': signal.signal_id,
            'signal_type': signal.signal_type,
            'confidence_score': signal.confidence_score,
            'block_number': signal.block_number,
            'profit_estimate': signal.profit_estimate,
            'addresses_involved': signal.addresses_involved,
            'metadata': signal.metadata
        }
        
        self.audit_logger.log_access(
            user='mev_agent',
            resource='mev_detection',
            action='DETECT_SIGNAL',
            result='SUCCESS',
            metadata=audit_entry
        )
    
    async def _store_signal_in_graph(self, signal: MEVSignal):
        """Store MEV signal in Neo4j graph"""
        with self.neo4j_client.driver.session() as session:
            # Create MEV signal node
            query = """
            CREATE (s:MEVSignal {
                signal_id: $signal_id,
                signal_type: $signal_type,
                confidence_score: $confidence_score,
                block_number: $block_number,
                profit_estimate: $profit_estimate,
                timestamp: datetime()
            })
            """
            
            session.run(query, 
                signal_id=signal.signal_id,
                signal_type=signal.signal_type,
                confidence_score=signal.confidence_score,
                block_number=signal.block_number,
                profit_estimate=signal.profit_estimate
            )
            
            # Connect to involved addresses
            for address in signal.addresses_involved:
                if address:
                    rel_query = """
                    MATCH (s:MEVSignal {signal_id: $signal_id})
                    MERGE (w:Wallet {address: $address})
                    MERGE (s)-[:INVOLVES]->(w)
                    """
                    session.run(rel_query, signal_id=signal.signal_id, address=address)
    
    async def _send_alert(self, signal: MEVSignal):
        """Send alert for high-confidence MEV signal"""
        alert_data = {
            'type': 'mev_detection',
            'severity': 'high' if signal.confidence_score > 0.8 else 'medium',
            'signal_id': signal.signal_id,
            'signal_type': signal.signal_type,
            'confidence_score': signal.confidence_score,
            'block_number': signal.block_number,
            'profit_estimate': signal.profit_estimate,
            'addresses_involved': signal.addresses_involved,
            'timestamp': signal.timestamp.isoformat()
        }
        
        # Send to alert system (could be Slack, email, etc.)
        print(f"MEV ALERT: {alert_data}")
        
        # In real implementation, this would send to notification service
        # await self.notification_service.send_alert(alert_data)
    
    async def _update_risk_scores(self, signal: MEVSignal):
        """Update risk scores for involved addresses"""
        for address in signal.addresses_involved:
            if address:
                # Calculate new risk score
                risk_score = self._calculate_risk_score(address, signal)
                
                # Update in Neo4j
                with self.neo4j_client.driver.session() as session:
                    query = """
                    MATCH (w:Wallet {address: $address})
                    SET w.risk_score = $risk_score,
                        w.last_mev_activity = datetime()
                    """
                    session.run(query, address=address, risk_score=risk_score)
    
    def _calculate_risk_score(self, address: str, signal: MEVSignal) -> float:
        """Calculate risk score for an address based on MEV activity"""
        # Base risk score
        base_score = 0.1
        
        # Add risk based on signal type
        if signal.signal_type == 'SANDWICH_ATTACK':
            base_score += 0.3
        elif signal.signal_type == 'LIQUIDATION':
            base_score += 0.2
        
        # Add risk based on confidence
        base_score += signal.confidence_score * 0.2
        
        # Add risk based on profit
        if signal.profit_estimate > 1.0:  # More than 1 ETH
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    async def _get_latest_block(self) -> Optional[Dict[str, Any]]:
        """Get latest block data (mock implementation)"""
        # In real implementation, this would fetch from blockchain
        return {
            'number': 18500000,
            'timestamp': int(datetime.now().timestamp()),
            'transactions': [
                # Mock transaction data
            ]
        }
    
    async def get_mev_statistics(self, time_range: str = '24h') -> Dict[str, Any]:
        """Get MEV statistics for the specified time range"""
        with self.neo4j_client.driver.session() as session:
            query = """
            MATCH (s:MEVSignal)
            WHERE s.timestamp > datetime() - duration({hours: 24})
            RETURN 
                count(s) as total_signals,
                avg(s.confidence_score) as avg_confidence,
                sum(s.profit_estimate) as total_profit,
                s.signal_type as signal_type,
                count(s) as count
            """
            
            result = session.run(query)
            stats = {
                'total_signals': 0,
                'avg_confidence': 0.0,
                'total_profit': 0.0,
                'by_type': {}
            }
            
            for record in result:
                stats['total_signals'] += record['count']
                stats['total_profit'] += record['total_profit']
                stats['by_type'][record['signal_type']] = record['count']
            
            if stats['total_signals'] > 0:
                stats['avg_confidence'] = stats['avg_confidence'] / stats['total_signals']
            
            return stats
```

### **Day 3-4: Whale Tracking**

#### **Step 1: Create Whale Tracker**
**File:** `services/agents/whale_tracker.py`

```python
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

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
```

### **Day 5-7: Risk Scoring Models**

#### **Step 1: Create Risk Scoring System**
**File:** `services/risk_ai/risk_scorer.py`

```python
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

class RiskScorer:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.feature_names = [
            'transaction_count',
            'total_volume_eth',
            'avg_transaction_value',
            'max_transaction_value',
            'gas_price_volatility',
            'contract_interaction_ratio',
            'unique_counterparties',
            'mev_activity_score',
            'whale_movement_score',
            'sanctions_risk_score',
            'age_days',
            'balance_volatility'
        ]
        self.model_path = 'models/risk_scorer.pkl'
        self.scaler_path = 'models/risk_scaler.pkl'
        
        # Load pre-trained model if exists
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained model and scaler"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print("Loaded pre-trained risk scoring model")
    
    def extract_risk_features(self, address: str, address_data: Dict[str, Any]) -> List[float]:
        """Extract risk features for an address"""
        features = []
        
        # Transaction-based features
        features.append(address_data.get('transaction_count', 0))
        features.append(address_data.get('total_volume_eth', 0))
        features.append(address_data.get('avg_transaction_value', 0))
        features.append(address_data.get('max_transaction_value', 0))
        
        # Gas price volatility
        gas_prices = address_data.get('gas_prices', [])
        if gas_prices:
            features.append(np.std(gas_prices))
        else:
            features.append(0)
        
        # Contract interaction ratio
        total_txs = address_data.get('transaction_count', 1)
        contract_txs = address_data.get('contract_interactions', 0)
        features.append(contract_txs / total_txs if total_txs > 0 else 0)
        
        # Unique counterparties
        features.append(address_data.get('unique_counterparties', 0))
        
        # MEV activity score
        features.append(address_data.get('mev_activity_score', 0))
        
        # Whale movement score
        features.append(address_data.get('whale_movement_score', 0))
        
        # Sanctions risk score
        features.append(address_data.get('sanctions_risk_score', 0))
        
        # Age in days
        features.append(address_data.get('age_days', 0))
        
        # Balance volatility
        balance_history = address_data.get('balance_history', [])
        if balance_history:
            features.append(np.std(balance_history))
        else:
            features.append(0)
        
        return features
    
    def calculate_risk_score(self, address: str, address_data: Dict[str, Any]) -> float:
        """Calculate risk score for an address"""
        features = self.extract_risk_features(address, address_data)
        
        # Normalize features
        features_scaled = self.scaler.transform([features])
        
        # Predict risk score
        risk_score = self.model.predict(features_scaled)[0]
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, risk_score))
    
    def train_model(self, training_data: List[Dict[str, Any]]):
        """Train the risk scoring model"""
        X = []
        y = []
        
        for data_point in training_data:
            features = self.extract_risk_features(data_point['address'], data_point['address_data'])
            X.append(features)
            y.append(data_point['risk_score'])
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model trained - MSE: {mse:.4f}, R²: {r2:.4f}")
        
        # Save model
        self._save_model()
        
        return {'mse': mse, 'r2': r2}
    
    def _save_model(self):
        """Save trained model and scaler"""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print("Model saved successfully")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the model"""
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))
    
    def explain_risk_score(self, address: str, address_data: Dict[str, Any]) -> Dict[str, Any]:
        """Explain the risk score for an address"""
        features = self.extract_risk_features(address, address_data)
        feature_importance = self.get_feature_importance()
        
        # Calculate contribution of each feature
        contributions = {}
        for i, feature_name in enumerate(self.feature_names):
            importance = feature_importance[feature_name]
            value = features[i]
            contributions[feature_name] = {
                'value': value,
                'importance': importance,
                'contribution': value * importance
            }
        
        # Sort by contribution
        sorted_contributions = sorted(
            contributions.items(), 
            key=lambda x: abs(x[1]['contribution']), 
            reverse=True
        )
        
        return {
            'address': address,
            'risk_score': self.calculate_risk_score(address, address_data),
            'feature_contributions': dict(sorted_contributions[:5]),  # Top 5 features
            'risk_factors': self._identify_risk_factors(contributions)
        }
    
    def _identify_risk_factors(self, contributions: Dict[str, Dict[str, float]]) -> List[str]:
        """Identify main risk factors"""
        risk_factors = []
        
        for feature_name, data in contributions.items():
            if abs(data['contribution']) > 0.1:  # Significant contribution
                if data['contribution'] > 0:
                    risk_factors.append(f"High {feature_name.replace('_', ' ')}")
                else:
                    risk_factors.append(f"Low {feature_name.replace('_', ' ')}")
        
        return risk_factors[:3]  # Top 3 risk factors
```

---

## 📋 **WEEK 6: SANCTIONS & COMPLIANCE**

### **Day 1-3: OFAC Sanctions Screening**

#### **Step 1: Create Sanctions Checker**
**File:** `services/access_control/sanctions_checker.py`

```python
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json

@dataclass
class SanctionsResult:
    address: str
    is_sanctioned: bool
    sanctions_list: List[str]
    confidence_score: float
    last_checked: datetime
    metadata: Dict[str, Any]

class SanctionsChecker:
    def __init__(self):
        self.sanctions_cache = {}
        self.api_endpoints = {
            'chainalysis': 'https://api.chainalysis.com/api/risk/v2/entities/',
            'elliptic': 'https://api.elliptic.co/v2/risk/',
            'crystal': 'https://api.crystalblockchain.com/risk/'
        }
        self.api_keys = {
            'chainalysis': os.getenv('CHAINALYSIS_API_KEY'),
            'elliptic': os.getenv('ELLIPTIC_API_KEY'),
            'crystal': os.getenv('CRYSTAL_API_KEY')
        }
        
        # Known sanctioned addresses
        self.known_sanctioned = {
            '0x7F367cC41522cE07553e823bf3be79A889DEbe1B',  # Tornado Cash
            '0x722122dF12D4e14e13Ac3b6895a86e84145b6967',  # Tornado Cash
            '0xDD4c48C0B24039969fC16D1cdF626eaB821d3384',  # Tornado Cash
            '0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b',  # Tornado Cash
            '0x722122dF12D4e14e13Ac3b6895a86e84145b6967',  # Tornado Cash
        }
    
    async def check_address(self, address: str) -> SanctionsResult:
        """Check if an address is sanctioned"""
        # Check cache first
        if address in self.sanctions_cache:
            cached_result = self.sanctions_cache[address]
            if (datetime.now() - cached_result.last_checked).days < 1:
                return cached_result
        
        # Check known sanctioned addresses
        if address.lower() in self.known_sanctioned:
            result = SanctionsResult(
                address=address,
                is_sanctioned=True,
                sanctions_list=['OFAC', 'Tornado Cash'],
                confidence_score=1.0,
                last_checked=datetime.now(),
                metadata={'source': 'known_list'}
            )
            self.sanctions_cache[address] = result
            return result
        
        # Check external APIs
        sanctions_list = []
        confidence_scores = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # Chainalysis check
            if self.api_keys['chainalysis']:
                tasks.append(self._check_chainalysis(session, address))
            
            # Elliptic check
            if self.api_keys['elliptic']:
                tasks.append(self._check_elliptic(session, address))
            
            # Crystal check
            if self.api_keys['crystal']:
                tasks.append(self._check_crystal(session, address))
            
            # Wait for all checks to complete
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, dict) and result.get('sanctions'):
                        sanctions_list.extend(result['sanctions'])
                        confidence_scores.append(result.get('confidence', 0.5))
        
        # Determine final result
        is_sanctioned = len(sanctions_list) > 0
        confidence_score = np.mean(confidence_scores) if confidence_scores else 0.0
        
        result = SanctionsResult(
            address=address,
            is_sanctioned=is_sanctioned,
            sanctions_list=list(set(sanctions_list)),  # Remove duplicates
            confidence_score=confidence_score,
            last_checked=datetime.now(),
            metadata={'sources_checked': len(tasks)}
        )
        
        # Cache result
        self.sanctions_cache[address] = result
        
        return result
    
    async def _check_chainalysis(self, session: aiohttp.ClientSession, address: str) -> Dict[str, Any]:
        """Check address