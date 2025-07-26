from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List, Optional, Dict, Any
from .resolvers import GraphQLResolvers
from .schema import schema
from ..entity_resolution.pipeline import EntityResolutionPipeline
import logging

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Onchain Graph API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Add GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")

# Initialize entity resolution pipeline
entity_pipeline = EntityResolutionPipeline()

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "graph-api"}

# Add metrics endpoint
@app.get("/metrics")
async def get_metrics():
    resolvers = GraphQLResolvers()
    return resolvers.neo4j_client.get_metrics()

# Add wallet endpoints
@app.get("/wallets/{address}")
async def get_wallet(address: str):
    """Get wallet information"""
    try:
        resolvers = GraphQLResolvers()
        wallet = resolvers.neo4j_client.get_wallet(address)
        if wallet:
            return wallet
        else:
            raise HTTPException(status_code=404, detail="Wallet not found")
    except Exception as e:
        logger.error(f"Error getting wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add entity resolution endpoints
@app.get("/entity-resolution/sample")
async def get_sample_entity_resolution():
    """Get sample entity resolution data"""
    try:
        # Process sample data
        sample_transactions = [
            {
                'hash': '0x1234567890abcdef',
                'from': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
                'to': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'value': 1.5,
                'gasPrice': 25,
                'gasUsed': 21000,
                'blockNumber': 18000000,
                'timestamp': 1700000000,
                'status': True,
                'chainId': 1,
                'input': '0x'
            },
            {
                'hash': '0xabcdef1234567890',
                'from': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'to': '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6',
                'value': 0.5,
                'gasPrice': 30,
                'gasUsed': 21000,
                'blockNumber': 18000001,
                'timestamp': 1700000060,
                'status': True,
                'chainId': 1,
                'input': '0x'
            }
        ]
        
        clusters = await entity_pipeline.process_new_transactions(sample_transactions)
        
        return {
            'transactions_processed': len(sample_transactions),
            'clusters_found': len(clusters),
            'clusters': clusters
        }
    except Exception as e:
        logger.error(f"Error in sample entity resolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/entity-resolution/process")
async def process_entity_resolution(transactions: List[Dict[str, Any]]):
    """Process transactions for entity resolution"""
    try:
        clusters = await entity_pipeline.process_new_transactions(transactions)
        
        return {
            'transactions_processed': len(transactions),
            'clusters_found': len(clusters),
            'clusters': clusters
        }
    except Exception as e:
        logger.error(f"Error in entity resolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entity-resolution/real-data")
async def process_real_data(limit: int = 50):
    """Process real blockchain data for entity resolution"""
    try:
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("latest", limit)
        await entity_pipeline.cleanup()
        
        return result
    except Exception as e:
        logger.error(f"Error processing real data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entity-resolution/whale-data")
async def process_whale_data():
    """Process whale transaction data for entity resolution"""
    try:
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("whale")
        await entity_pipeline.cleanup()
        
        return result
    except Exception as e:
        logger.error(f"Error processing whale data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/entity-resolution/mev-data")
async def process_mev_data():
    """Process MEV transaction data for entity resolution"""
    try:
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("mev")
        await entity_pipeline.cleanup()
        
        return result
    except Exception as e:
        logger.error(f"Error processing MEV data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add entity search endpoint
@app.post("/entities/search")
async def search_entities(query: str, limit: int = 10):
    """Search entities by query"""
    try:
        resolvers = GraphQLResolvers()
        entities = resolvers.neo4j_client.search_entities(query, limit)
        return {'entities': entities, 'query': query, 'limit': limit}
    except Exception as e:
        logger.error(f"Error searching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add graph analysis endpoints
@app.get("/graph/analysis/patterns")
async def analyze_graph_patterns():
    """Analyze graph patterns and relationships"""
    try:
        resolvers = GraphQLResolvers()
        metrics = resolvers.neo4j_client.get_metrics()
        
        return {
            'total_nodes': metrics.get('wallets', 0) + metrics.get('entities', 0),
            'total_relationships': metrics.get('relationships', 0),
            'entities': metrics.get('entities', 0),
            'wallets': metrics.get('wallets', 0),
            'status': metrics.get('status', 'unknown')
        }
    except Exception as e:
        logger.error(f"Error analyzing graph patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/analysis/clusters")
async def analyze_clusters():
    """Analyze entity clusters"""
    try:
        stats = await entity_pipeline.get_entity_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error analyzing clusters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add development endpoints
@app.post("/dev/create-wallet")
async def create_wallet(address: str):
    """Create a wallet node for development"""
    try:
        resolvers = GraphQLResolvers()
        result = resolvers.neo4j_client.create_wallet_node(address, {
            'created_at': '2024-01-01T00:00:00Z',
            'source': 'dev_endpoint'
        })
        return {'success': True, 'address': address, 'result': result is not None}
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dev/create-relationship")
async def create_relationship(from_address: str, to_address: str, tx_hash: str):
    """Create a transaction relationship for development"""
    try:
        resolvers = GraphQLResolvers()
        result = resolvers.neo4j_client.create_transaction_relationship(
            from_address, to_address, tx_hash, {
                'created_at': '2024-01-01T00:00:00Z',
                'source': 'dev_endpoint'
            }
        )
        return {'success': True, 'from': from_address, 'to': to_address, 'result': result is not None}
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add multi-chain endpoint
@app.get("/multi-chain/latest")
async def get_multi_chain_latest():
    """Get latest data from multiple chains"""
    try:
        # For now, return Ethereum data
        await entity_pipeline.initialize()
        result = await entity_pipeline.process_real_data("latest", 10)
        await entity_pipeline.cleanup()
        
        return {
            'ethereum': result,
            'polygon': {'status': 'not_implemented'},
            'arbitrum': {'status': 'not_implemented'},
            'optimism': {'status': 'not_implemented'}
        }
    except Exception as e:
        logger.error(f"Error getting multi-chain data: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 