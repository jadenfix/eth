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
    
    def export_graph_data(self) -> Dict[str, Any]:
        """Export graph data for validation"""
        if not self.driver:
            return {
                "nodes": 5,
                "relationships": 10,
                "entities": [
                    {"entity_id": "mock_1", "type": "exchange"},
                    {"entity_id": "mock_2", "type": "wallet"}
                ]
            }
        
        with self.driver.session() as session:
            # Get node counts
            nodes_result = session.run("MATCH (n) RETURN count(n) as count")
            nodes_count = nodes_result.single()["count"]
            
            # Get relationship counts
            rels_result = session.run("MATCH ()-[r]-() RETURN count(r) as count")
            rels_count = rels_result.single()["count"]
            
            # Get sample entities
            entities_result = session.run("""
                MATCH (e:TestEntity)
                RETURN e.entity_id as entity_id, e.entity_type as entity_type
                LIMIT 10
            """)
            entities = [{"entity_id": record["entity_id"], "type": record["entity_type"]} 
                       for record in entities_result]
            
            return {
                "nodes": nodes_count,
                "relationships": rels_count,
                "entities": entities
            }
