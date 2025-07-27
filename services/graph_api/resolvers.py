"""
GraphQL Resolvers for Entity Resolution and Graph Database
"""

import strawberry
from typing import List, Optional, Dict, Any
from .neo4j_client import Neo4jClient
import logging

logger = logging.getLogger(__name__)

@strawberry.type
class Wallet:
    address: str
    balance: Optional[float]
    transaction_count: int
    first_seen: Optional[str]
    last_seen: Optional[str]

@strawberry.type
class Transaction:
    hash: str
    from_address: str
    to_address: str
    value: float
    gas_price: float
    block_number: int
    timestamp: str

@strawberry.type
class Entity:
    id: str
    name: str
    addresses: List[str]
    confidence_score: float
    transaction_count: int
    total_value: float

@strawberry.type
class Cluster:
    id: str
    addresses: List[str]
    size: int
    confidence_score: float
    patterns: List[str]

@strawberry.type
class GraphMetrics:
    total_wallets: int
    total_transactions: int
    total_entities: int
    total_clusters: int
    avg_cluster_size: float

@strawberry.type
class Query:
    @strawberry.field
    def wallet(self, address: str) -> Optional[Wallet]:
        """Get wallet information"""
        try:
            neo4j_client = Neo4jClient()
            wallet_data = neo4j_client.get_wallet(address)
            if wallet_data:
                return Wallet(
                    address=wallet_data.get('address', address),
                    balance=wallet_data.get('balance', 0.0),
                    transaction_count=wallet_data.get('transaction_count', 0),
                    first_seen=wallet_data.get('first_seen'),
                    last_seen=wallet_data.get('last_seen')
                )
            return None
        except Exception as e:
            logger.error(f"Error getting wallet {address}: {e}")
            return None
    
    @strawberry.field
    def wallets(self, limit: int = 10, offset: int = 0) -> List[Wallet]:
        """Get list of wallets"""
        try:
            neo4j_client = Neo4jClient()
            wallets_data = neo4j_client.get_wallets(limit, offset)
            return [
                Wallet(
                    address=w.get('address', ''),
                    balance=w.get('balance', 0.0),
                    transaction_count=w.get('transaction_count', 0),
                    first_seen=w.get('first_seen'),
                    last_seen=w.get('last_seen')
                )
                for w in wallets_data
            ]
        except Exception as e:
            logger.error(f"Error getting wallets: {e}")
            return []
    
    @strawberry.field
    def entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity information"""
        try:
            neo4j_client = Neo4jClient()
            entity_data = neo4j_client.get_entity(entity_id)
            if entity_data:
                return Entity(
                    id=entity_data.get('id', entity_id),
                    name=entity_data.get('name', ''),
                    addresses=entity_data.get('addresses', []),
                    confidence_score=entity_data.get('confidence_score', 0.0),
                    transaction_count=entity_data.get('transaction_count', 0),
                    total_value=entity_data.get('total_value', 0.0)
                )
            return None
        except Exception as e:
            logger.error(f"Error getting entity {entity_id}: {e}")
            return None
    
    @strawberry.field
    def entities(self, limit: int = 10, offset: int = 0) -> List[Entity]:
        """Get list of entities"""
        try:
            neo4j_client = Neo4jClient()
            entities_data = neo4j_client.get_entities(limit, offset)
            return [
                Entity(
                    id=e.get('id', ''),
                    name=e.get('name', ''),
                    addresses=e.get('addresses', []),
                    confidence_score=e.get('confidence_score', 0.0),
                    transaction_count=e.get('transaction_count', 0),
                    total_value=e.get('total_value', 0.0)
                )
                for e in entities_data
            ]
        except Exception as e:
            logger.error(f"Error getting entities: {e}")
            return []
    
    @strawberry.field
    def search_entities(self, query: str, limit: int = 10) -> List[Entity]:
        """Search entities by query"""
        try:
            neo4j_client = Neo4jClient()
            search_results = neo4j_client.search_entities(query, limit)
            return [
                Entity(
                    id=e.get('id', ''),
                    name=e.get('name', ''),
                    addresses=e.get('addresses', []),
                    confidence_score=e.get('confidence_score', 0.0),
                    transaction_count=e.get('transaction_count', 0),
                    total_value=e.get('total_value', 0.0)
                )
                for e in search_results
            ]
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []
    
    @strawberry.field
    def clusters(self, limit: int = 10) -> List[Cluster]:
        """Get entity clusters"""
        try:
            neo4j_client = Neo4jClient()
            clusters_data = neo4j_client.get_clusters(limit)
            return [
                Cluster(
                    id=c.get('id', ''),
                    addresses=c.get('addresses', []),
                    size=c.get('size', 0),
                    confidence_score=c.get('confidence_score', 0.0),
                    patterns=c.get('patterns', [])
                )
                for c in clusters_data
            ]
        except Exception as e:
            logger.error(f"Error getting clusters: {e}")
            return []
    
    @strawberry.field
    def metrics(self) -> GraphMetrics:
        """Get graph metrics"""
        try:
            neo4j_client = Neo4jClient()
            metrics_data = neo4j_client.get_metrics()
            return GraphMetrics(
                total_wallets=metrics_data.get('wallets', 0),
                total_transactions=metrics_data.get('transactions', 0),
                total_entities=metrics_data.get('entities', 0),
                total_clusters=metrics_data.get('clusters', 0),
                avg_cluster_size=metrics_data.get('avg_cluster_size', 0.0)
            )
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return GraphMetrics(
                total_wallets=0,
                total_transactions=0,
                total_entities=0,
                total_clusters=0,
                avg_cluster_size=0.0
            )

# Create the schema
schema = strawberry.Schema(query=Query) 