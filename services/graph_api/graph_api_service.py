#!/usr/bin/env python3
"""
Graph API Service with WebSocket Support
Provides GraphQL API and real-time subscriptions for Neo4j data
"""
import os
import json
import asyncio
import websockets
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging
from datetime import datetime
from google.cloud import bigquery

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Graph API Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GraphAPIService:
    def __init__(self):
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_user = os.getenv('NEO4J_USER')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        # Initialize Neo4j driver
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # Initialize BigQuery client
        self.bq_client = bigquery.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
        
        # WebSocket connections
        self.connections = set()
        
    def query_neo4j(self, query, parameters=None):
        """Execute Neo4j query"""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def sync_to_neo4j(self, entity_data):
        """Sync data from BigQuery to Neo4j"""
        with self.driver.session() as session:
            # Create or update entity
            query = """
            MERGE (e:Entity {id: $entity_id})
            SET e.address = $address,
                e.entity_type = $entity_type,
                e.updated_at = datetime()
            RETURN e
            """
            session.run(query, entity_data)
            logger.info(f"✅ Synced entity {entity_data.get('entity_id')} to Neo4j")
    
    async def broadcast_update(self, data):
        """Broadcast updates to all WebSocket connections"""
        if self.connections:
            message = json.dumps(data)
            await asyncio.gather(
                *[conn.send(message) for conn in self.connections],
                return_exceptions=True
            )

# Initialize service
graph_service = GraphAPIService()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Neo4j connection
        result = graph_service.query_neo4j("RETURN 1 as test")
        return {"status": "healthy", "neo4j": "connected", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/graph/entities")
async def get_entities():
    """Get all entities from Neo4j"""
    try:
        query = """
        MATCH (e:Entity)
        RETURN e.id as entity_id, e.address as address, e.entity_type as type, e.updated_at as updated
        LIMIT 100
        """
        entities = graph_service.query_neo4j(query)
        return {"entities": entities, "count": len(entities)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/graph/relationships")
async def get_relationships():
    """Get entity relationships"""
    try:
        query = """
        MATCH (a:Entity)-[r]->(b:Entity)
        RETURN a.id as from_entity, type(r) as relationship, b.id as to_entity
        LIMIT 100
        """
        relationships = graph_service.query_neo4j(query)
        return {"relationships": relationships, "count": len(relationships)}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/graph/sync")
async def sync_data():
    """Trigger BigQuery to Neo4j sync"""
    try:
        # Query recent transactions from BigQuery
        query = f"""
        SELECT DISTINCT from_address, to_address, block_number
        FROM `{os.getenv('GOOGLE_CLOUD_PROJECT')}.{os.getenv('BIGQUERY_DATASET')}.{os.getenv('BIGQUERY_TABLE_RAW')}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
        ORDER BY block_number DESC
        LIMIT 50
        """
        
        query_job = graph_service.bq_client.query(query)
        results = query_job.result()
        
        synced_count = 0
        for row in results:
            # Sync from_address
            if row.from_address:
                entity_data = {
                    'entity_id': f"addr_{row.from_address}",
                    'address': row.from_address,
                    'entity_type': 'wallet'
                }
                graph_service.sync_to_neo4j(entity_data)
                synced_count += 1
                
            # Sync to_address 
            if row.to_address:
                entity_data = {
                    'entity_id': f"addr_{row.to_address}",
                    'address': row.to_address,
                    'entity_type': 'wallet'
                }
                graph_service.sync_to_neo4j(entity_data)
                synced_count += 1
        
        # Broadcast update
        await graph_service.broadcast_update({
            "type": "sync_complete",
            "synced_entities": synced_count,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"status": "success", "synced_entities": synced_count}
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        return {"error": str(e)}

@app.websocket("/subscriptions")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    graph_service.connections.add(websocket)
    logger.info(f"WebSocket connected. Total connections: {len(graph_service.connections)}")
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection_ack",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive
        while True:
            # Send periodic heartbeat
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            })
            await asyncio.sleep(30)
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        graph_service.connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(graph_service.connections)}")

if __name__ == "__main__":
    logger.info("🚀 Starting Graph API Service...")
    logger.info(f"Neo4j URI: {os.getenv('NEO4J_URI')}")
    logger.info(f"Server will run on: http://localhost:4000")
    logger.info(f"WebSocket endpoint: ws://localhost:4000/subscriptions")
    
    uvicorn.run(app, host="0.0.0.0", port=4000)
