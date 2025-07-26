import os
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.connected = False
        
        try:
            if self.uri and self.user and self.password:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                # Test connection
                with self.driver.session() as session:
                    session.run("RETURN 1")
                self.connected = True
                logger.info("✅ Neo4j connected successfully")
            else:
                logger.warning("⚠️ Neo4j credentials not found in environment variables")
                self.connected = False
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            self.connected = False
    
    def close(self):
        if hasattr(self, 'driver') and self.connected:
            self.driver.close()
    
    def create_wallet_node(self, address: str, metadata: Dict[str, Any] = None):
        """Create a wallet node in Neo4j"""
        if not self.connected:
            logger.warning("Neo4j not connected, skipping wallet creation")
            return None
            
        try:
            with self.driver.session() as session:
                query = """
                MERGE (w:Wallet {address: $address})
                SET w += $metadata
                RETURN w
                """
                result = session.run(query, address=address, metadata=metadata or {})
                return result.single()
        except Exception as e:
            logger.error(f"Error creating wallet node: {e}")
            return None
    
    def create_transaction_relationship(
        self, 
        from_address: str, 
        to_address: str, 
        tx_hash: str,
        metadata: Dict[str, Any] = None
    ):
        """Create a transaction relationship between wallets"""
        if not self.connected:
            logger.warning("Neo4j not connected, skipping relationship creation")
            return None
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (from:Wallet {address: $from_address})
                MATCH (to:Wallet {address: $to_address})
                MERGE (from)-[r:TRANSACTED_WITH {tx_hash: $tx_hash}]->(to)
                SET r += $metadata
                RETURN r
                """
                result = session.run(
                    query, 
                    from_address=from_address,
                    to_address=to_address,
                    tx_hash=tx_hash,
                    metadata=metadata or {}
                )
                return result.single()
        except Exception as e:
            logger.error(f"Error creating transaction relationship: {e}")
            return None
    
    def create_entity_cluster(self, entity_id: str, addresses: List[str], metadata: Dict[str, Any] = None):
        """Create an entity cluster with multiple addresses"""
        if not self.connected:
            logger.warning("Neo4j not connected, skipping entity cluster creation")
            return None
            
        try:
            with self.driver.session() as session:
                query = """
                MERGE (e:Entity {id: $entity_id})
                SET e += $metadata
                
                WITH e
                UNWIND $addresses AS address
                MERGE (w:Wallet {address: address})
                MERGE (e)-[:OWNS]->(w)
                
                RETURN e
                """
                result = session.run(
                    query,
                    entity_id=entity_id,
                    addresses=addresses,
                    metadata=metadata or {}
                )
                return result.single()
        except Exception as e:
            logger.error(f"Error creating entity cluster: {e}")
            return None
    
    def get_wallet(self, address: str) -> Optional[Dict[str, Any]]:
        """Get wallet by address"""
        if not self.connected:
            logger.warning("Neo4j not connected, cannot get wallet")
            return None
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (w:Wallet {address: $address})
                OPTIONAL MATCH (w)-[:OWNS]-(e:Entity)
                RETURN w, e
                """
                result = session.run(query, address=address)
                record = result.single()
                
                if record:
                    return {
                        'address': record['w']['address'],
                        'metadata': dict(record['w']),
                        'entity': dict(record['e']) if record['e'] else None
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting wallet: {e}")
            return None
    
    def get_entities(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get entities with pagination"""
        if not self.connected:
            logger.warning("Neo4j not connected, cannot get entities")
            return []
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (e:Entity)
                RETURN e
                ORDER BY e.confidence_score DESC
                SKIP $offset
                LIMIT $limit
                """
                result = session.run(query, limit=limit, offset=offset)
                entities = []
                
                for record in result:
                    entities.append({
                        'id': record['e']['id'],
                        'metadata': dict(record['e'])
                    })
                
                return entities
        except Exception as e:
            logger.error(f"Error getting entities: {e}")
            return []
    
    def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities by query"""
        if not self.connected:
            logger.warning("Neo4j not connected, cannot search entities")
            return []
            
        try:
            with self.driver.session() as session:
                query = """
                MATCH (e:Entity)
                WHERE e.id CONTAINS $query
                   OR e.labels CONTAINS $query
                   OR EXISTS((e)-[:OWNS]->(w:Wallet WHERE w.address CONTAINS $query))
                RETURN e
                LIMIT $limit
                """
                result = session.run(query, query=query, limit=limit)
                entities = []
                
                for record in result:
                    entities.append({
                        'id': record['e']['id'],
                        'metadata': dict(record['e'])
                    })
                
                return entities
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get database metrics"""
        if not self.connected:
            return {
                "entities": 0,
                "wallets": 0,
                "relationships": 0,
                "status": "disconnected"
            }
            
        try:
            with self.driver.session() as session:
                # Count entities
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()['count']
                
                # Count wallets
                wallet_count = session.run("MATCH (w:Wallet) RETURN count(w) as count").single()['count']
                
                # Count relationships
                relationship_count = session.run("MATCH ()-[r]-() RETURN count(r) as count").single()['count']
                
                return {
                    "entities": entity_count,
                    "wallets": wallet_count,
                    "relationships": relationship_count,
                    "status": "connected"
                }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {
                "entities": 0,
                "wallets": 0,
                "relationships": 0,
                "status": "error"
            } 