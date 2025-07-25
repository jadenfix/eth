"""
Neo4j testing utilities
"""

import os
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class Neo4jTestUtils:
    """Utilities for Neo4j graph database testing"""
    
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = None
        self._initialize_driver()
    
    def _initialize_driver(self):
        """Initialize Neo4j driver with error handling"""
        try:
            # Import neo4j here to handle missing dependency gracefully
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info("Neo4j driver initialized")
        except ImportError:
            logger.warning("Neo4j driver not available - using mock implementation")
            self.driver = None
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e} - using mock implementation")
            self.driver = None
    
    def close(self):
        """Close Neo4j driver"""
        if self.driver:
            self.driver.close()
    
    def clear_test_data(self):
        """Clear all test data from Neo4j"""
        if not self.driver:
            logger.info("Mock: Cleared test data from Neo4j")
            return
        
        with self.driver.session() as session:
            # Delete all nodes and relationships with test labels
            session.run("MATCH (n) WHERE any(label in labels(n) WHERE label STARTS WITH 'Test') DETACH DELETE n")
            logger.info("Cleared test data from Neo4j")
    
    def load_ontology(self, ontology_data: List[Dict[str, Any]]) -> int:
        """Load ontology entities and relationships"""
        if not self.driver:
            logger.info(f"Mock: Loaded {len(ontology_data)} ontology entities")
            return len(ontology_data)
        
        nodes_created = 0
        with self.driver.session() as session:
            for entity in ontology_data:
                # Create entity node
                query = """
                CREATE (e:TestEntity {
                    entity_id: $entity_id,
                    entity_type: $entity_type,
                    institution: $institution,
                    created_at: datetime()
                })
                """
                session.run(query, {
                    "entity_id": entity.get("entity_id", f"test_entity_{nodes_created}"),
                    "entity_type": entity.get("entity_type", "address"),
                    "institution": entity.get("institution", "unknown")
                })
                
                # Create address nodes and relationships
                for address in entity.get("addresses", []):
                    address_query = """
                    MATCH (e:TestEntity {entity_id: $entity_id})
                    CREATE (a:TestAddress {address: $address})
                    CREATE (e)-[:OWNS]->(a)
                    """
                    session.run(address_query, {
                        "entity_id": entity.get("entity_id", f"test_entity_{nodes_created}"),
                        "address": address
                    })
                
                nodes_created += 1
        
        logger.info(f"Loaded {nodes_created} ontology entities to Neo4j")
        return nodes_created
    
    def load_entities(self, entities: List[Dict[str, Any]]) -> int:
        """Load entities into Neo4j (alias for load_ontology for compatibility)"""
        if not self.driver:
            logger.info(f"Mock: Loaded {len(entities)} entities")
            return len(entities)
        
        nodes_created = 0
        with self.driver.session() as session:
            for entity in entities:
                # Create address node with all properties
                # Build dynamic properties from entity dict
                properties = {
                    "address": entity.get("address"),
                    "type": entity.get("type", "wallet"),
                    "risk_score": entity.get("risk_score", 0.0),
                    "total_volume": entity.get("total_volume", 0),
                    "fixture_id": entity.get("fixture_id", "test")
                }
                
                # Add any additional properties
                for key, value in entity.items():
                    if key not in ["address", "type", "risk_score", "total_volume", "fixture_id"]:
                        properties[key] = value
                
                # Build dynamic query - use MERGE to prevent duplicates
                prop_pairs = [f"{k}: ${k}" for k in properties.keys()]
                query = f"""
                MERGE (a:TestAddress {{address: $address, fixture_id: $fixture_id}})
                SET a += {{{', '.join([f'{k}: ${k}' for k in properties.keys() if k not in ['address', 'fixture_id']])}}}
                """
                session.run(query, properties)
                nodes_created += 1
        
        logger.info(f"Loaded {nodes_created} entities to Neo4j")
        return nodes_created
    
    def load_relationships(self, relationships: List[Dict[str, Any]]) -> int:
        """Load relationships into Neo4j"""
        if not self.driver:
            logger.info(f"Mock: Loaded {len(relationships)} relationships")
            return len(relationships)
        
        rels_created = 0
        with self.driver.session() as session:
            for rel in relationships:
                # Create relationship between addresses - use MERGE to prevent duplicates
                query = """
                MATCH (a:TestAddress {address: $from_address})
                MATCH (b:TestAddress {address: $to_address})
                MERGE (a)-[r:TestRelationship {fixture_id: $fixture_id}]->(b)
                SET r.relationship_type = $relationship_type,
                    r.transaction_count = $transaction_count,
                    r.total_value = $total_value,
                    r.weight = $weight
                """
                session.run(query, {
                    "from_address": rel.get("from_address"),
                    "to_address": rel.get("to_address"),
                    "relationship_type": rel.get("relationship_type", "RELATED_TO"),
                    "transaction_count": rel.get("transaction_count", 0),
                    "total_value": rel.get("total_value", 0),
                    "weight": rel.get("weight", 0.0),
                    "fixture_id": rel.get("fixture_id", "test")
                })
                rels_created += 1
        
        logger.info(f"Loaded {rels_created} relationships to Neo4j")
        return rels_created
    
    def query_graph(self, query: str) -> List[Dict[str, Any]]:
        """Execute Cypher query and return results"""
        if not self.driver:
            # Return mock data for testing
            logger.info(f"Mock: Executed query: {query}")
            return [
                {
                    "from_addr": "0xMOCK123",
                    "to_addr": "0xMOCK456", 
                    "rel_type": "INTERACTED_WITH",
                    "tx_count": 5,
                    "from_risk": 0.3,
                    "to_risk": 0.7
                },
                {
                    "from_addr": "0xMOCK456",
                    "to_addr": "0xMOCK789",
                    "rel_type": "SENT_TO", 
                    "tx_count": 2,
                    "from_risk": 0.7,
                    "to_risk": 0.1
                }
            ]
        
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID"""
        if not self.driver:
            return {
                "entity_id": entity_id,
                "entity_type": "address",
                "addresses": ["0xMOCK123"],
                "institution": "Mock Exchange"
            }
        
        with self.driver.session() as session:
            query = """
            MATCH (e:TestEntity {entity_id: $entity_id})
            OPTIONAL MATCH (e)-[:OWNS]->(a:TestAddress)
            RETURN e, collect(a.address) as addresses
            """
            result = session.run(query, {"entity_id": entity_id})
            record = result.single()
            
            if record:
                entity = record["e"]
                return {
                    "entity_id": entity["entity_id"],
                    "entity_type": entity["entity_type"],
                    "institution": entity["institution"],
                    "addresses": record["addresses"]
                }
            
            return None
    
    def get_entity_links(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get relationships for an entity"""
        if not self.driver:
            return [
                {"type": "OWNS", "target": "0xMOCK123"},
                {"type": "OWNS", "target": "0xMOCK456"}
            ]
        
        with self.driver.session() as session:
            query = """
            MATCH (e:TestEntity {entity_id: $entity_id})-[r]-(target)
            RETURN type(r) as relationship_type, target
            """
            result = session.run(query, {"entity_id": entity_id})
            
            relationships = []
            for record in result:
                relationships.append({
                    "type": record["relationship_type"],
                    "target": dict(record["target"])
                })
            
            return relationships
    
    def create_entity_relationship(self, entity1_id: str, entity2_id: str, relationship_type: str) -> bool:
        """Create relationship between entities"""
        if not self.driver:
            logger.info(f"Mock: Created {relationship_type} relationship between {entity1_id} and {entity2_id}")
            return True
        
        with self.driver.session() as session:
            query = f"""
            MATCH (e1:TestEntity {{entity_id: $entity1_id}})
            MATCH (e2:TestEntity {{entity_id: $entity2_id}})
            CREATE (e1)-[:{relationship_type}]->(e2)
            """
            result = session.run(query, {
                "entity1_id": entity1_id,
                "entity2_id": entity2_id
            })
            
            return result.consume().counters.relationships_created > 0
    
    def query_entities_by_institution(self, institution: str) -> List[Dict[str, Any]]:
        """Query entities by institution"""
        if not self.driver:
            return [
                {
                    "entity_id": "mock_entity_1",
                    "entity_type": "exchange",
                    "institution": institution,
                    "addresses": ["0xMOCK123", "0xMOCK456"]
                }
            ]
        
        with self.driver.session() as session:
            query = """
            MATCH (e:TestEntity {institution: $institution})
            OPTIONAL MATCH (e)-[:OWNS]->(a:TestAddress)
            RETURN e, collect(a.address) as addresses
            """
            result = session.run(query, {"institution": institution})
            
            entities = []
            for record in result:
                entity = record["e"]
                entities.append({
                    "entity_id": entity["entity_id"],
                    "entity_type": entity["entity_type"],
                    "institution": entity["institution"],
                    "addresses": record["addresses"]
                })
            
            return entities
    
    def get_node_count(self, label: str = "TestEntity") -> int:
        """Get count of nodes with specific label"""
        if not self.driver:
            return 5  # Mock count
        
        with self.driver.session() as session:
            query = f"MATCH (n:{label}) RETURN count(n) as count"
            result = session.run(query)
            record = result.single()
            return record["count"] if record else 0
    
    def get_relationship_count(self, relationship_type: Optional[str] = None) -> int:
        """Get count of relationships"""
        if not self.driver:
            return 10  # Mock count
        
        with self.driver.session() as session:
            if relationship_type:
                query = f"MATCH ()-[r:{relationship_type}]-() RETURN count(r) as count"
            else:
                query = "MATCH ()-[r]-() RETURN count(r) as count"
            
            result = session.run(query)
            record = result.single()
            return record["count"] if record else 0
    
    def export_graph_data(self, filter_condition: str = None) -> Dict[str, Any]:
        """Export graph data with optional filter"""
        if not self.driver:
            logger.info(f"Mock: Exported graph data with filter: {filter_condition}")
            return {
                "nodes": [
                    {"id": "0xMOCK123", "type": "wallet", "risk_score": 0.3},
                    {"id": "0xMOCK456", "type": "contract", "risk_score": 0.7},
                    {"id": "0xMOCK789", "type": "wallet", "risk_score": 0.1}
                ],
                "relationships": [
                    {"from": "0xMOCK123", "to": "0xMOCK456", "type": "INTERACTED_WITH"},
                    {"from": "0xMOCK456", "to": "0xMOCK789", "type": "SENT_TO"}
                ],
                "metadata": {
                    "node_count": 3,
                    "relationship_count": 2,
                    "export_timestamp": "2024-01-01T00:00:00Z"
                }
            }
        
        # Build query with optional filter
        if filter_condition:
            # Parse the filter condition to extract the fixture_id value
            if "fixture_id = '" in filter_condition:
                fixture_id = filter_condition.split("fixture_id = '")[1].split("'")[0]
                base_query = """
                MATCH (n:TestAddress {fixture_id: $fixture_id})
                OPTIONAL MATCH (n)-[r:TestRelationship {fixture_id: $fixture_id}]->(m:TestAddress {fixture_id: $fixture_id})
                RETURN DISTINCT n.address as node_id, n.type as node_type, n.risk_score as risk_score,
                       r.relationship_type as rel_type, m.address as target_id
                """
                params = {"fixture_id": fixture_id}
            else:
                base_query = """
                MATCH (n:TestAddress)
                OPTIONAL MATCH (n)-[r:TestRelationship]->(m:TestAddress)
                RETURN n.address as node_id, n.type as node_type, n.risk_score as risk_score,
                       r.relationship_type as rel_type, m.address as target_id
                """
                params = {}
        else:
            base_query = """
            MATCH (n:TestAddress)
            OPTIONAL MATCH (n)-[r:TestRelationship]->(m:TestAddress)
            RETURN n.address as node_id, n.type as node_type, n.risk_score as risk_score,
                   r.relationship_type as rel_type, m.address as target_id
            """
            params = {}
        
        with self.driver.session() as session:
            result = session.run(base_query, params)
            records = [dict(record) for record in result]
            
            # Process into nodes and relationships
            nodes = []
            relationships = []
            node_ids = set()
            relationship_ids = set()  # Track unique relationships
            
            for record in records:
                if record["node_id"] and record["node_id"] not in node_ids:
                    nodes.append({
                        "id": record["node_id"],
                        "type": record["node_type"],
                        "risk_score": record["risk_score"]
                    })
                    node_ids.add(record["node_id"])
                
                if record["target_id"] and record["rel_type"]:
                    # Create unique relationship ID to avoid duplicates
                    rel_id = f"{record['node_id']}-{record['rel_type']}-{record['target_id']}"
                    if rel_id not in relationship_ids:
                        relationships.append({
                            "from": record["node_id"],
                            "to": record["target_id"],
                            "type": record["rel_type"]
                        })
                        relationship_ids.add(rel_id)
            
            return {
                "nodes": nodes,
                "relationships": relationships,
                "metadata": {
                    "node_count": len(nodes),
                    "relationship_count": len(relationships),
                    "export_timestamp": "2024-01-01T00:00:00Z"
                }
            }
