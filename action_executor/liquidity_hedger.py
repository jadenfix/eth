import asyncio
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import numpy as np
import logging
from neo4j import GraphDatabase
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

@dataclass
class HedgePosition:
    hedge_id: str
    risk_amount: float
    hedge_amount: float
    hedge_token: str
    risk_token: str
    hedge_ratio: float
    status: str  # 'active', 'closed', 'expired'
    created_at: datetime
    closed_at: Optional[datetime] = None
    pnl: Optional[float] = None

class LiquidityHedger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize hedges storage
        self.hedges = {}
        
        # Initialize real database connections
        self._init_databases()
        
        # DeFi protocol contracts for hedging
        self.hedge_contracts = {
            'USDC': '0xA0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8',
            'USDT': '0xB0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8',
            'DAI': '0xC0b86a33E6441b8c4C8C8C8C8C8C8C8C8C8C8C8'
        }
        
        # Default hedge ratios
        self.default_hedge_ratios = {
            'ETH': 0.8,  # Hedge 80% of ETH exposure
            'BTC': 0.7,  # Hedge 70% of BTC exposure
            'USDC': 0.5, # Hedge 50% of USDC exposure
            'USDT': 0.5, # Hedge 50% of USDT exposure
            'DAI': 0.5   # Hedge 50% of DAI exposure
        }
    
    def _init_databases(self):
        """Initialize real database connections"""
        try:
            # Initialize Neo4j for hedge position graph relationships
            self.neo4j_uri = os.getenv('NEO4J_URI')
            self.neo4j_user = os.getenv('NEO4J_USER')
            self.neo4j_password = os.getenv('NEO4J_PASSWORD')
            
            if self.neo4j_uri and self.neo4j_user and self.neo4j_password:
                self.neo4j_driver = GraphDatabase.driver(
                    self.neo4j_uri, 
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                self.logger.info("✅ Neo4j connected for hedge position management")
            else:
                self.neo4j_driver = None
                self.logger.warning("⚠️ Neo4j credentials not found, using local storage")
            
            # Initialize BigQuery for hedge analytics
            self.bq_project = os.getenv('GOOGLE_CLOUD_PROJECT')
            if self.bq_project:
                self.bq_client = bigquery.Client(project=self.bq_project)
                self.logger.info("✅ BigQuery connected for hedge analytics")
            else:
                self.bq_client = None
                self.logger.warning("⚠️ BigQuery project not found, analytics disabled")
                
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            self.neo4j_driver = None
            self.bq_client = None
    
    async def create_hedge_position(self, hedge_position: HedgePosition) -> bool:
        """Create a new hedge position"""
        try:
            # Store in Neo4j for graph relationships
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    CREATE (h:HedgePosition {
                        hedge_id: $hedge_id,
                        risk_amount: $risk_amount,
                        hedge_amount: $hedge_amount,
                        hedge_token: $hedge_token,
                        risk_token: $risk_token,
                        hedge_ratio: $hedge_ratio,
                        status: $status,
                        created_at: datetime(),
                        closed_at: $closed_at,
                        pnl: $pnl
                    })
                    """
                    session.run(query,
                        hedge_id=hedge_position.hedge_id,
                        risk_amount=hedge_position.risk_amount,
                        hedge_amount=hedge_position.hedge_amount,
                        hedge_token=hedge_position.hedge_token,
                        risk_token=hedge_position.risk_token,
                        hedge_ratio=hedge_position.hedge_ratio,
                        status=hedge_position.status,
                        closed_at=hedge_position.closed_at.isoformat() if hedge_position.closed_at else None,
                        pnl=hedge_position.pnl
                    )
            
            # Store in BigQuery for analytics
            if self.bq_client:
                table_id = f"{self.bq_project}.onchain_data.hedge_positions"
                rows_to_insert = [{
                    'hedge_id': hedge_position.hedge_id,
                    'risk_amount': hedge_position.risk_amount,
                    'hedge_amount': hedge_position.hedge_amount,
                    'hedge_token': hedge_position.hedge_token,
                    'risk_token': hedge_position.risk_token,
                    'hedge_ratio': hedge_position.hedge_ratio,
                    'status': hedge_position.status,
                    'created_at': hedge_position.created_at.isoformat(),
                    'closed_at': hedge_position.closed_at.isoformat() if hedge_position.closed_at else None,
                    'pnl': hedge_position.pnl
                }]
                
                errors = self.bq_client.insert_rows_json(table_id, rows_to_insert)
                if errors:
                    self.logger.error(f"Failed to insert hedge position into BigQuery: {errors}")
                    return False
            
            self.logger.info(f"Hedge position created: {hedge_position.hedge_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create hedge position: {e}")
            return False
    
    async def calculate_hedge_amount(self, risk_amount: float, risk_token: str) -> float:
        """Calculate optimal hedge amount based on risk"""
        try:
            # Get hedge ratio for the token
            hedge_ratio = self.default_hedge_ratios.get(risk_token, 0.5)
            
            # Calculate hedge amount
            hedge_amount = risk_amount * hedge_ratio
            
            # Apply risk adjustments based on market conditions
            # This would integrate with price feeds and volatility data
            market_volatility = await self._get_market_volatility(risk_token)
            hedge_amount *= (1 + market_volatility * 0.1)  # Adjust for volatility
            
            return hedge_amount
            
        except Exception as e:
            self.logger.error(f"Failed to calculate hedge amount: {e}")
            return risk_amount * 0.5  # Default to 50% hedge
    
    async def execute_hedge(self, risk_amount: float, risk_token: str, hedge_token: str = 'USDC') -> Optional[HedgePosition]:
        """Execute a hedge position"""
        try:
            # Calculate hedge amount
            hedge_amount = await self.calculate_hedge_amount(risk_amount, risk_token)
            
            # Create hedge position
            hedge_position = HedgePosition(
                hedge_id=f"hedge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                risk_amount=risk_amount,
                hedge_amount=hedge_amount,
                hedge_token=hedge_token,
                risk_token=risk_token,
                hedge_ratio=hedge_amount / risk_amount,
                status='active',
                created_at=datetime.now()
            )
            
            # Store in database
            success = await self.create_hedge_position(hedge_position)
            if not success:
                return None
            
            # Execute on-chain hedge (simulated)
            on_chain_success = await self._execute_on_chain_hedge(hedge_position)
            if not on_chain_success:
                # Mark as failed
                await self.update_hedge_status(hedge_position.hedge_id, 'failed')
                return None
            
            self.logger.info(f"Hedge executed: {hedge_position.hedge_id}")
            return hedge_position
            
        except Exception as e:
            self.logger.error(f"Failed to execute hedge: {e}")
            return None
    
    async def close_hedge_position(self, hedge_id: str, pnl: Optional[float] = None) -> bool:
        """Close a hedge position"""
        try:
            closed_at = datetime.now()
            
            # Update in Neo4j
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (h:HedgePosition {hedge_id: $hedge_id})
                    SET h.status = 'closed',
                        h.closed_at = datetime(),
                        h.pnl = $pnl
                    RETURN h
                    """
                    result = session.run(query, hedge_id=hedge_id, pnl=pnl)
                    if not result.single():
                        self.logger.error(f"Hedge position not found: {hedge_id}")
                        return False
            
            # Update in BigQuery
            if self.bq_client:
                table_id = f"{self.bq_project}.onchain_data.hedge_positions"
                query = f"""
                UPDATE `{table_id}`
                SET status = 'closed',
                    closed_at = TIMESTAMP('{closed_at.isoformat()}'),
                    pnl = {pnl if pnl is not None else 'NULL'}
                WHERE hedge_id = '{hedge_id}'
                """
                self.bq_client.query(query)
            
            self.logger.info(f"Hedge position closed: {hedge_id} - PnL: {pnl}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close hedge position: {e}")
            return False
    
    async def get_hedge_position(self, hedge_id: str) -> Optional[HedgePosition]:
        """Get hedge position by ID"""
        try:
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (h:HedgePosition {hedge_id: $hedge_id})
                    RETURN h
                    """
                    result = session.run(query, hedge_id=hedge_id)
                    record = result.single()
                    
                    if record:
                        data = record['h']
                        # Handle datetime conversion - Neo4j returns datetime objects, not strings
                        created_at = data['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at)
                        
                        closed_at = data.get('closed_at')
                        if closed_at and isinstance(closed_at, str):
                            closed_at = datetime.fromisoformat(closed_at)
                        
                        return HedgePosition(
                            hedge_id=data['hedge_id'],
                            risk_amount=data['risk_amount'],
                            hedge_amount=data['hedge_amount'],
                            hedge_token=data['hedge_token'],
                            risk_token=data['risk_token'],
                            hedge_ratio=data['hedge_ratio'],
                            status=data['status'],
                            created_at=created_at,
                            closed_at=closed_at,
                            pnl=data.get('pnl')
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get hedge position: {e}")
            return None
    
    async def get_active_hedges(self) -> List[HedgePosition]:
        """Get all active hedge positions"""
        try:
            positions = []
            
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (h:HedgePosition {status: 'active'})
                    RETURN h
                    """
                    result = session.run(query)
                    
                    for record in result:
                        data = record['h']
                        # Handle datetime conversion - Neo4j returns datetime objects, not strings
                        created_at = data['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at)
                        
                        closed_at = data.get('closed_at')
                        if closed_at and isinstance(closed_at, str):
                            closed_at = datetime.fromisoformat(closed_at)
                        
                        position = HedgePosition(
                            hedge_id=data['hedge_id'],
                            risk_amount=data['risk_amount'],
                            hedge_amount=data['hedge_amount'],
                            hedge_token=data['hedge_token'],
                            risk_token=data['risk_token'],
                            hedge_ratio=data['hedge_ratio'],
                            status=data['status'],
                            created_at=created_at,
                            closed_at=closed_at,
                            pnl=data.get('pnl')
                        )
                        positions.append(position)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to get active hedges: {e}")
            return []
    
    async def calculate_total_hedge_exposure(self) -> float:
        """Calculate total hedge exposure"""
        try:
            active_hedges = await self.get_active_hedges()
            total_exposure = sum(h.hedge_amount for h in active_hedges)
            return total_exposure
            
        except Exception as e:
            self.logger.error(f"Failed to calculate total hedge exposure: {e}")
            return 0.0
    
    async def get_hedge_performance_summary(self) -> Dict[str, Any]:
        """Get hedge performance summary"""
        try:
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (h:HedgePosition)
                    WHERE h.status = 'closed' AND h.pnl IS NOT NULL
                    RETURN 
                        count(h) as total_closed,
                        avg(h.pnl) as avg_pnl,
                        sum(h.pnl) as total_pnl,
                        min(h.pnl) as min_pnl,
                        max(h.pnl) as max_pnl
                    """
                    result = session.run(query)
                    record = result.single()
                    
                    if record:
                        return {
                            'total_closed_hedges': record['total_closed'],
                            'average_pnl': record['avg_pnl'],
                            'total_pnl': record['total_pnl'],
                            'min_pnl': record['min_pnl'],
                            'max_pnl': record['max_pnl']
                        }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Failed to get hedge performance summary: {e}")
            return {}
    
    async def update_hedge_status(self, hedge_id: str, status: str) -> bool:
        """Update hedge position status"""
        try:
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (h:HedgePosition {hedge_id: $hedge_id})
                    SET h.status = $status
                    RETURN h
                    """
                    result = session.run(query, hedge_id=hedge_id, status=status)
                    return result.single() is not None
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update hedge status: {e}")
            return False
    
    async def _execute_on_chain_hedge(self, hedge_position: HedgePosition) -> bool:
        """Execute hedge on blockchain"""
        try:
            # This would be the actual on-chain hedge execution
            # For now, simulate success
            
            # In real implementation:
            # 1. Create hedge transaction
            # 2. Sign with admin key
            # 3. Send to blockchain
            # 4. Wait for confirmation
            
            self.logger.info(f"Executing on-chain hedge: {hedge_position.hedge_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to execute on-chain hedge: {e}")
            return False
    
    async def _get_market_volatility(self, token: str) -> float:
        """Get market volatility for a token"""
        try:
            # This would integrate with price feeds and volatility data
            # For now, return a simple volatility estimate
            
            # Simulate different volatilities for different tokens
            volatilities = {
                'ETH': 0.3,   # High volatility
                'BTC': 0.25,  # High volatility
                'USDC': 0.01, # Low volatility
                'USDT': 0.01, # Low volatility
                'DAI': 0.01   # Low volatility
            }
            
            return volatilities.get(token, 0.1)
            
        except Exception as e:
            self.logger.error(f"Failed to get market volatility: {e}")
            return 0.1  # Default volatility
    
    async def create_hedge(self, hedge_params: dict) -> HedgePosition:
        """Create new hedge"""
        try:
            hedge_id = f"hedge_{len(self.hedges) + 1}"
            
            # Handle both dict and keyword arguments
            if isinstance(hedge_params, dict):
                hedge_data = hedge_params
            else:
                hedge_data = hedge_params
            
            # Create HedgePosition object
            hedge_position = HedgePosition(
                hedge_id=hedge_id,
                risk_amount=hedge_data.get('risk_amount', 0.0),
                hedge_amount=hedge_data.get('hedge_amount', 0.0),
                hedge_token=hedge_data.get('hedge_token', 'USDC'),
                risk_token=hedge_data.get('risk_token', 'ETH'),
                hedge_ratio=hedge_data.get('hedge_ratio', 0.5),
                status='pending',
                created_at=datetime.now()
            )
            
            self.hedges[hedge_id] = hedge_position
            return hedge_position
        except Exception as e:
            self.logger.error(f"Failed to create hedge: {e}")
            return None
    
    async def execute_hedge(self, hedge_id: str) -> bool:
        """Execute hedge"""
        try:
            if hedge_id in self.hedges:
                self.hedges[hedge_id]['status'] = 'executed'
                self.hedges[hedge_id]['executed_at'] = datetime.now()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to execute hedge: {e}")
            return False
    
    async def monitor_hedge(self, hedge_id: str) -> dict:
        """Monitor hedge status"""
        try:
            return self.hedges.get(hedge_id, {})
        except Exception as e:
            self.logger.error(f"Failed to monitor hedge: {e}")
            return {}
    
    async def get_hedge_recommendations(self, risk_amount: float, risk_token: str) -> List[Dict[str, Any]]:
        """Get hedge recommendations based on risk parameters"""
        try:
            recommendations = []
            
            # Calculate optimal hedge amount
            hedge_amount = await self.calculate_hedge_amount(risk_amount, risk_token)
            
            # Get market volatility
            volatility = await self._get_market_volatility(risk_token)
            
            # Generate recommendations for different hedge tokens
            hedge_tokens = ['USDC', 'USDT', 'DAI']
            
            for hedge_token in hedge_tokens:
                recommendation = {
                    'hedge_token': hedge_token,
                    'hedge_amount': hedge_amount,
                    'risk_amount': risk_amount,
                    'risk_token': risk_token,
                    'hedge_ratio': self.default_hedge_ratios.get(risk_token, 0.5),
                    'volatility': volatility,
                    'confidence_score': 0.8
                }
                recommendations.append(recommendation)
            
            self.logger.info(f"Generated {len(recommendations)} hedge recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get hedge recommendations: {e}")
            return []
    
    async def get_hedge_performance(self) -> Dict[str, Any]:
        """Get hedge performance metrics"""
        try:
            active_hedges = await self.get_active_hedges()
            
            total_hedge_value = sum(hedge.hedge_amount for hedge in active_hedges)
            total_risk_value = sum(hedge.risk_amount for hedge in active_hedges)
            
            performance = {
                'total_active_hedges': len(active_hedges),
                'total_hedge_value': total_hedge_value,
                'total_risk_value': total_risk_value,
                'hedge_ratio': total_hedge_value / total_risk_value if total_risk_value > 0 else 0,
                'average_hedge_size': total_hedge_value / len(active_hedges) if active_hedges else 0
            }
            
            self.logger.info(f"Hedge performance calculated: {performance}")
            return performance
            
        except Exception as e:
            self.logger.error(f"Failed to get hedge performance: {e}")
            return {} 