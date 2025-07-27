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
from typing import Dict, List, Any, Optional
from datetime import datetime
from .mev_detector import MEVDetector, MEVSignal
from ..graph_api.neo4j_client import Neo4jClient
from ..access_control.audit_sink import AuditLogger
import logging

logger = logging.getLogger(__name__)

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
        
        logger.info("MEV Agent started monitoring...")
    
    async def stop_monitoring(self):
        """Stop MEV monitoring"""
        self.is_running = False
        logger.info("MEV Agent stopped monitoring...")
    
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
                logger.error(f"Error monitoring blocks: {e}")
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
                logger.error(f"Error processing signal: {e}")
    
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
            logger.error(f"Error handling signal: {e}")
    
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
        if not self.neo4j_client.connected:
            logger.warning("Neo4j not connected, skipping signal storage")
            return
            
        try:
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
                        
        except Exception as e:
            logger.error(f"Error storing signal in graph: {e}")
    
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
        logger.info(f"MEV ALERT: {alert_data}")
        
        # In real implementation, this would send to notification service
        # await self.notification_service.send_alert(alert_data)
    
    async def _update_risk_scores(self, signal: MEVSignal):
        """Update risk scores for involved addresses"""
        for address in signal.addresses_involved:
            if address:
                # Calculate new risk score
                risk_score = self._calculate_risk_score(address, signal)
                
                # Update in Neo4j
                if self.neo4j_client.connected:
                    try:
                        with self.neo4j_client.driver.session() as session:
                            query = """
                            MATCH (w:Wallet {address: $address})
                            SET w.risk_score = $risk_score,
                                w.last_mev_activity = datetime()
                            """
                            session.run(query, address=address, risk_score=risk_score)
                    except Exception as e:
                        logger.error(f"Error updating risk score: {e}")
    
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
        if not self.neo4j_client.connected:
            return {
                'total_signals': 0,
                'avg_confidence': 0.0,
                'total_profit': 0.0,
                'by_type': {}
            }
            
        try:
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
                
        except Exception as e:
            logger.error(f"Error getting MEV statistics: {e}")
            return {
                'total_signals': 0,
                'avg_confidence': 0.0,
                'total_profit': 0.0,
                'by_type': {}
            }
    
    async def process_sample_transactions(self, transactions: List[Dict[str, Any]]) -> List[MEVSignal]:
        """Process sample transactions for MEV detection"""
        return await self._analyze_block({'transactions': transactions})
