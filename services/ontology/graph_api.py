"""
Ontology Service - GraphQL API for blockchain semantic layer.

Manages entities, relationships, and metadata for blockchain addresses,
contracts, and transactions. Provides Palantir-style semantic querying.
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

import structlog
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync
from ariadne.constants import PLAYGROUND_HTML
from neo4j import GraphDatabase
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse

# Configure logging
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

# GraphQL Schema Definition
type_defs = """
    type Query {
        entity(id: String!): Entity
        entities(filter: EntityFilter): [Entity!]!
        relationship(id: String!): Relationship
        relationships(from: String, to: String, type: String): [Relationship!]!
        searchEntities(query: String!): [Entity!]!
        getEntityNetwork(id: String!, depth: Int = 2): EntityNetwork!
    }
    
    type Mutation {
        createEntity(input: EntityInput!): Entity!
        updateEntity(id: String!, input: EntityUpdateInput!): Entity!
        createRelationship(input: RelationshipInput!): Relationship!
        mergeEntities(sourceId: String!, targetId: String!): Entity!
    }
    
    type Entity {
        id: String!
        type: EntityType!
        address: String
        name: String
        labels: [String!]!
        properties: JSON
        relationships: [Relationship!]!
        riskScore: Float
        createdAt: String!
        updatedAt: String!
    }
    
    type Relationship {
        id: String!
        type: RelationshipType!
        fromEntity: Entity!
        toEntity: Entity!
        properties: JSON
        weight: Float
        createdAt: String!
    }
    
    type EntityNetwork {
        center: Entity!
        nodes: [Entity!]!
        edges: [Relationship!]!
        depth: Int!
    }
    
    enum EntityType {
        ADDRESS
        CONTRACT
        TOKEN
        EXCHANGE
        POOL
        BRIDGE
        ORGANIZATION
        PERSON
    }
    
    enum RelationshipType {
        OWNS
        CONTROLS
        TRANSACTS_WITH
        DEPLOYED
        INTERACTS_WITH
        PART_OF
        SIMILAR_TO
        RELATED_TO
    }
    
    input EntityFilter {
        type: EntityType
        labels: [String!]
        hasAddress: Boolean
        riskScoreMin: Float
        riskScoreMax: Float
    }
    
    input EntityInput {
        type: EntityType!
        address: String
        name: String
        labels: [String!]
        properties: JSON
    }
    
    input EntityUpdateInput {
        name: String
        labels: [String!]
        properties: JSON
        riskScore: Float
    }
    
    input RelationshipInput {
        type: RelationshipType!
        fromEntityId: String!
        toEntityId: String!
        properties: JSON
        weight: Float
    }
    
    scalar JSON
"""

# GraphQL Resolvers
query = QueryType()
mutation = MutationType()


class OntologyService:
    """Neo4j-backed ontology service."""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        self.logger = logger.bind(service="ontology")
        
    def close(self):
        self.driver.close()
        
    def create_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity in the graph."""
        with self.driver.session() as session:
            result = session.run(
                """
                CREATE (e:Entity:$type {
                    id: $id,
                    type: $type,
                    address: $address,
                    name: $name,
                    labels: $labels,
                    properties: $properties,
                    riskScore: $riskScore,
                    createdAt: datetime(),
                    updatedAt: datetime()
                })
                RETURN e
                """,
                id=entity_data['id'],
                type=entity_data['type'],
                address=entity_data.get('address'),
                name=entity_data.get('name'),
                labels=entity_data.get('labels', []),
                properties=entity_data.get('properties', {}),
                riskScore=entity_data.get('riskScore', 0.0)
            )
            record = result.single()
            return dict(record['e'])
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID."""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (e:Entity {id: $id}) RETURN e",
                id=entity_id
            )
            record = result.single()
            if record:
                return dict(record['e'])
            return None
    
    def get_entities(self, filter_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get entities with optional filtering."""
        query_parts = ["MATCH (e:Entity)"]
        params = {}
        
        where_conditions = []
        if filter_params.get('type'):
            where_conditions.append("e.type = $type")
            params['type'] = filter_params['type']
            
        if filter_params.get('labels'):
            where_conditions.append("ANY(label IN $labels WHERE label IN e.labels)")
            params['labels'] = filter_params['labels']
            
        if filter_params.get('hasAddress'):
            where_conditions.append("e.address IS NOT NULL")
            
        if filter_params.get('riskScoreMin'):
            where_conditions.append("e.riskScore >= $riskScoreMin")
            params['riskScoreMin'] = filter_params['riskScoreMin']
            
        if filter_params.get('riskScoreMax'):
            where_conditions.append("e.riskScore <= $riskScoreMax")
            params['riskScoreMax'] = filter_params['riskScoreMax']
        
        if where_conditions:
            query_parts.append("WHERE " + " AND ".join(where_conditions))
            
        query_parts.append("RETURN e ORDER BY e.updatedAt DESC LIMIT 100")
        
        with self.driver.session() as session:
            result = session.run(" ".join(query_parts), **params)
            return [dict(record['e']) for record in result]
    
    def create_relationship(self, rel_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create relationship between entities."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (from:Entity {id: $fromId}), (to:Entity {id: $toId})
                CREATE (from)-[r:$relType {
                    id: $id,
                    type: $relType,
                    properties: $properties,
                    weight: $weight,
                    createdAt: datetime()
                }]->(to)
                RETURN r, from, to
                """,
                fromId=rel_data['fromEntityId'],
                toId=rel_data['toEntityId'],
                relType=rel_data['type'],
                id=rel_data['id'],
                properties=rel_data.get('properties', {}),
                weight=rel_data.get('weight', 1.0)
            )
            record = result.single()
            if record:
                return {
                    'relationship': dict(record['r']),
                    'fromEntity': dict(record['from']),
                    'toEntity': dict(record['to'])
                }
            return None
    
    def get_entity_network(self, entity_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get entity network within specified depth."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = (center:Entity {id: $entityId})-[*1..$depth]-(node:Entity)
                WITH center, collect(DISTINCT node) as nodes, 
                     collect(DISTINCT relationships(path)) as relPaths
                UNWIND relPaths as relPath
                UNWIND relPath as rel
                WITH center, nodes, collect(DISTINCT rel) as relationships
                RETURN center, nodes, relationships
                """,
                entityId=entity_id,
                depth=depth
            )
            
            record = result.single()
            if record:
                return {
                    'center': dict(record['center']),
                    'nodes': [dict(node) for node in record['nodes']],
                    'edges': [dict(rel) for rel in record['relationships']],
                    'depth': depth
                }
            return None


# Initialize service
ontology_service = OntologyService()


# GraphQL Resolvers
@query.field("entity")
def resolve_entity(_, info, id):
    return ontology_service.get_entity(id)


@query.field("entities")  
def resolve_entities(_, info, filter=None):
    return ontology_service.get_entities(filter or {})


@query.field("getEntityNetwork")
def resolve_entity_network(_, info, id, depth=2):
    return ontology_service.get_entity_network(id, depth)


@mutation.field("createEntity")
def resolve_create_entity(_, info, input):
    import uuid
    input['id'] = str(uuid.uuid4())
    return ontology_service.create_entity(input)


# Create executable schema
schema = make_executable_schema(type_defs, query, mutation)

# FastAPI app
app = FastAPI(title="Ontology Service")


@app.post("/graphql")
async def graphql_endpoint(request: Request):
    data = await request.json()
    success, result = graphql_sync(schema, data)
    return JSONResponse(result)


@app.get("/graphql")
async def graphql_playground():
    return HTMLResponse(PLAYGROUND_HTML)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ontology"}


@app.post("/edges/stream")
async def stream_cdc_acknowledgements(request: Request):
    """Stream CDC acknowledgements for bidirectional graph sync"""
    from google.cloud import pubsub_v1
    
    data = await request.json()
    
    # Publish change event to Pub/Sub for BigQuery sync
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(
        os.getenv("GCP_PROJECT_ID"), 
        "neo4j-change-events"
    )
    
    change_event = {
        "operation": data.get("operation", "UPDATE"),
        "entity_id": data.get("entity_id"),
        "entity_type": data.get("entity_type"),
        "changes": data.get("changes", {}),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Publish with attributes for filtering
    future = publisher.publish(
        topic_path,
        str(change_event).encode('utf-8'),
        operation=change_event["operation"],
        entity_type=change_event["entity_type"]
    )
    
    logger.info("Published Neo4j change event", 
               entity_id=data.get("entity_id"),
               operation=change_event["operation"])
    
    return {"status": "acknowledged", "message_id": future.result()}


@app.get("/sync/status")
async def get_sync_status():
    """Get bidirectional sync status between Neo4j and BigQuery"""
    # TODO: Implement actual sync monitoring
    return {
        "neo4j_to_bq": {
            "status": "healthy",
            "last_sync": datetime.utcnow().isoformat(),
            "lag_seconds": 45
        },
        "bq_to_neo4j": {
            "status": "healthy", 
            "last_sync": datetime.utcnow().isoformat(),
            "lag_seconds": 67
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
