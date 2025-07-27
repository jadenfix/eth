import asyncio
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from web3 import Web3
import json
import logging
from neo4j import GraphDatabase
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Position:
    address: str
    position_id: str
    asset: str
    amount: float
    value_usd: float
    risk_score: float
    status: str  # 'active', 'frozen', 'liquidated'
    created_at: datetime
    frozen_at: Optional[datetime] = None
    frozen_reason: Optional[str] = None

class PositionManager:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(os.getenv('ETHEREUM_RPC_URL', 'http://localhost:8545')))
        self.logger = logging.getLogger(__name__)
        
        # Initialize positions storage
        self.positions = {}
        
        # Initialize real database connections
        self._init_databases()
        
        # DeFi protocol contracts (would be real addresses in production)
        self.freeze_contracts = {
            'aave': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
            'compound': '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B',
            'uniswap': '0xE592427A0AEce92De3Edee1F18E0157C05861564'
        }
    
    def _init_databases(self):
        """Initialize real database connections"""
        try:
            # Initialize Neo4j for position graph relationships
            self.neo4j_uri = os.getenv('NEO4J_URI')
            self.neo4j_user = os.getenv('NEO4J_USER')
            self.neo4j_password = os.getenv('NEO4J_PASSWORD')
            
            if self.neo4j_uri and self.neo4j_user and self.neo4j_password:
                self.neo4j_driver = GraphDatabase.driver(
                    self.neo4j_uri, 
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                self.logger.info("✅ Neo4j connected for position management")
            else:
                self.neo4j_driver = None
                self.logger.warning("⚠️ Neo4j credentials not found, using local storage")
            
            # Initialize BigQuery for position analytics
            self.bq_project = os.getenv('GOOGLE_CLOUD_PROJECT')
            if self.bq_project:
                self.bq_client = bigquery.Client(project=self.bq_project)
                self.logger.info("✅ BigQuery connected for position analytics")
            else:
                self.bq_client = None
                self.logger.warning("⚠️ BigQuery project not found, analytics disabled")
                
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            self.neo4j_driver = None
            self.bq_client = None
    
    async def create_position(self, position: Position) -> bool:
        """Create a new position"""
        try:
            # Store in Neo4j for graph relationships
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    CREATE (p:Position {
                        position_id: $position_id,
                        address: $address,
                        asset: $asset,
                        amount: $amount,
                        value_usd: $value_usd,
                        risk_score: $risk_score,
                        status: $status,
                        created_at: datetime(),
                        frozen_at: $frozen_at,
                        frozen_reason: $frozen_reason
                    })
                    """
                    session.run(query,
                        position_id=position.position_id,
                        address=position.address,
                        asset=position.asset,
                        amount=position.amount,
                        value_usd=position.value_usd,
                        risk_score=position.risk_score,
                        status=position.status,
                        frozen_at=position.frozen_at.isoformat() if position.frozen_at else None,
                        frozen_reason=position.frozen_reason
                    )
            
            # Store in BigQuery for analytics
            if self.bq_client:
                table_id = f"{self.bq_project}.onchain_data.positions"
                rows_to_insert = [{
                    'position_id': position.position_id,
                    'address': position.address,
                    'asset': position.asset,
                    'amount': position.amount,
                    'value_usd': position.value_usd,
                    'risk_score': position.risk_score,
                    'status': position.status,
                    'created_at': position.created_at.isoformat(),
                    'frozen_at': position.frozen_at.isoformat() if position.frozen_at else None,
                    'frozen_reason': position.frozen_reason
                }]
                
                errors = self.bq_client.insert_rows_json(table_id, rows_to_insert)
                if errors:
                    self.logger.error(f"Failed to insert position into BigQuery: {errors}")
                    return False
            
            self.logger.info(f"Position created: {position.position_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create position: {e}")
            return False
    
    async def freeze_position(self, position_id: str, reason: str) -> bool:
        """Freeze a position"""
        try:
            frozen_at = datetime.now()
            
            # Update in Neo4j
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (p:Position {position_id: $position_id})
                    SET p.status = 'frozen',
                        p.frozen_at = datetime(),
                        p.frozen_reason = $reason
                    RETURN p
                    """
                    result = session.run(query, position_id=position_id, reason=reason)
                    if not result.single():
                        self.logger.error(f"Position not found: {position_id}")
                        return False
            
            # Update in BigQuery
            if self.bq_client:
                table_id = f"{self.bq_project}.onchain_data.positions"
                query = f"""
                UPDATE `{table_id}`
                SET status = 'frozen',
                    frozen_at = TIMESTAMP('{frozen_at.isoformat()}'),
                    frozen_reason = '{reason}'
                WHERE position_id = '{position_id}'
                """
                self.bq_client.query(query)
            
            self.logger.info(f"Position frozen: {position_id} - Reason: {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to freeze position: {e}")
            return False
    
    async def get_position(self, position_id: str) -> Optional[Position]:
        """Get position by ID"""
        try:
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (p:Position {position_id: $position_id})
                    RETURN p
                    """
                    result = session.run(query, position_id=position_id)
                    record = result.single()
                    
                    if record:
                        data = record['p']
                        # Handle datetime conversion - Neo4j returns datetime objects, not strings
                        created_at = data['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at)
                        
                        frozen_at = data.get('frozen_at')
                        if frozen_at and isinstance(frozen_at, str):
                            frozen_at = datetime.fromisoformat(frozen_at)
                        
                        return Position(
                            address=data['address'],
                            position_id=data['position_id'],
                            asset=data['asset'],
                            amount=data['amount'],
                            value_usd=data['value_usd'],
                            risk_score=data['risk_score'],
                            status=data['status'],
                            created_at=created_at,
                            frozen_at=frozen_at,
                            frozen_reason=data.get('frozen_reason')
                        )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get position: {e}")
            return None
    
    async def get_positions_by_address(self, address: str) -> List[Position]:
        """Get all positions for an address"""
        try:
            positions = []
            
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (p:Position {address: $address})
                    RETURN p
                    """
                    result = session.run(query, address=address)
                    
                    for record in result:
                        data = record['p']
                        # Handle datetime conversion - Neo4j returns datetime objects, not strings
                        created_at = data['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at)
                        
                        frozen_at = data.get('frozen_at')
                        if frozen_at and isinstance(frozen_at, str):
                            frozen_at = datetime.fromisoformat(frozen_at)
                        
                        position = Position(
                            address=data['address'],
                            position_id=data['position_id'],
                            asset=data['asset'],
                            amount=data['amount'],
                            value_usd=data['value_usd'],
                            risk_score=data['risk_score'],
                            status=data['status'],
                            created_at=created_at,
                            frozen_at=frozen_at,
                            frozen_reason=data.get('frozen_reason')
                        )
                        positions.append(position)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to get positions by address: {e}")
            return []
    
    async def get_frozen_positions(self) -> List[Position]:
        """Get all frozen positions"""
        try:
            positions = []
            
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (p:Position {status: 'frozen'})
                    RETURN p
                    """
                    result = session.run(query)
                    
                    for record in result:
                        data = record['p']
                        # Handle datetime conversion - Neo4j returns datetime objects, not strings
                        created_at = data['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at)
                        
                        frozen_at = data.get('frozen_at')
                        if frozen_at and isinstance(frozen_at, str):
                            frozen_at = datetime.fromisoformat(frozen_at)
                        
                        position = Position(
                            address=data['address'],
                            position_id=data['position_id'],
                            asset=data['asset'],
                            amount=data['amount'],
                            value_usd=data['value_usd'],
                            risk_score=data['risk_score'],
                            status=data['status'],
                            created_at=created_at,
                            frozen_at=frozen_at,
                            frozen_reason=data.get('frozen_reason')
                        )
                        positions.append(position)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to get frozen positions: {e}")
            return []
    
    async def calculate_total_exposure(self, address: str) -> float:
        """Calculate total exposure for an address"""
        try:
            positions = await self.get_positions_by_address(address)
            total_exposure = sum(p.value_usd for p in positions if p.status == 'active')
            return total_exposure
            
        except Exception as e:
            self.logger.error(f"Failed to calculate total exposure: {e}")
            return 0.0
    
    async def get_high_risk_positions(self, threshold: float = 0.8) -> List[Position]:
        """Get positions with high risk scores"""
        try:
            positions = []
            
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    query = """
                    MATCH (p:Position)
                    WHERE p.risk_score >= $threshold AND p.status = 'active'
                    RETURN p
                    ORDER BY p.risk_score DESC
                    """
                    result = session.run(query, threshold=threshold)
                    
                    for record in result:
                        data = record['p']
                        # Handle datetime conversion - Neo4j returns datetime objects, not strings
                        created_at = data['created_at']
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at)
                        
                        frozen_at = data.get('frozen_at')
                        if frozen_at and isinstance(frozen_at, str):
                            frozen_at = datetime.fromisoformat(frozen_at)
                        
                        position = Position(
                            address=data['address'],
                            position_id=data['position_id'],
                            asset=data['asset'],
                            amount=data['amount'],
                            value_usd=data['value_usd'],
                            risk_score=data['risk_score'],
                            status=data['status'],
                            created_at=created_at,
                            frozen_at=frozen_at,
                            frozen_reason=data.get('frozen_reason')
                        )
                        positions.append(position)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Failed to get high risk positions: {e}")
            return []
    
    async def get_position_risk_summary(self, position_id: str) -> Dict[str, Any]:
        """Get risk summary for a position"""
        try:
            position = await self.get_position(position_id)
            if not position:
                return {}
            
            return {
                'position_id': position_id,
                'risk_score': position.risk_score,
                'value_usd': position.value_usd,
                'status': position.status,
                'created_at': position.created_at.isoformat(),
                'frozen_at': position.frozen_at.isoformat() if position.frozen_at else None,
                'frozen_reason': position.frozen_reason
            }
        except Exception as e:
            self.logger.error(f"Failed to get position risk summary: {e}")
            return {} 