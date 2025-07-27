"""
Entity Resolution Pipeline for Phase 2 Implementation.

Matches and resolves blockchain addresses to known entities,
enriching the data with semantic identity information.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime
import numpy as np

from .entity_resolver import EntityResolver
from ..graph_api.neo4j_client import Neo4jClient
from ..ethereum_ingester.real_data_service import RealDataService

logger = logging.getLogger(__name__)

class EntityResolutionPipeline:
    def __init__(self):
        self.resolver = EntityResolver()
        self.neo4j_client = Neo4jClient()
        self.real_data_service = None
        
    async def initialize(self):
        """Initialize the pipeline with real data service"""
        if not self.real_data_service:
            self.real_data_service = RealDataService()
            await self.real_data_service.initialize()
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.real_data_service:
            await self.real_data_service.cleanup()
            
    async def process_sample_data(self) -> Dict[str, Any]:
        """Process sample data for entity resolution testing"""
        try:
            # Create sample transactions for testing
            sample_transactions = [
                {
                    "hash": "0x1234567890abcdef",
                    "from": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "to": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                    "value": 1.5,
                    "gasPrice": 25,
                    "gasUsed": 21000,
                    "blockNumber": 18000000,
                    "timestamp": 1700000000,
                    "status": True,
                    "chainId": 1,
                    "input": "0x"
                },
                {
                    "hash": "0xabcdef1234567890",
                    "from": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                    "to": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "value": 0.5,
                    "gasPrice": 30,
                    "gasUsed": 21000,
                    "blockNumber": 18000001,
                    "timestamp": 1700000060,
                    "status": True,
                    "chainId": 1,
                    "input": "0x"
                },
                {
                    "hash": "0x9876543210fedcba",
                    "from": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",
                    "to": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
                    "value": 2.0,
                    "gasPrice": 35,
                    "gasUsed": 50000,
                    "blockNumber": 18000002,
                    "timestamp": 1700000120,
                    "status": True,
                    "chainId": 1,
                    "input": "0xa9059cbb000000000000000000000000"
                }
            ]
            
            # Process the sample transactions
            result = await self.process_new_transactions(sample_transactions)
            
            return {
                "status": "success",
                "transactions_processed": len(sample_transactions),
                "clusters_found": len(result),
                "clusters": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing sample data: {e}")
            return {
                "status": "error",
                "error": str(e),
                "transactions_processed": 0,
                "clusters_found": 0,
                "clusters": {},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def process_new_transactions(self, transactions: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Process new transactions for entity resolution"""
        try:
            # Group transactions by address
            address_transactions = defaultdict(list)
            for tx in transactions:
                address_transactions[tx['from']].append(tx)
                if tx.get('to'):
                    address_transactions[tx['to']].append(tx)
            
            # Create wallet nodes in Neo4j
            for address in address_transactions.keys():
                metadata = {
                    'first_seen': datetime.utcnow().isoformat(),
                    'last_seen': datetime.utcnow().isoformat(),
                    'transaction_count': len(address_transactions[address])
                }
                self.neo4j_client.create_wallet_node(address, metadata)
            
            # Create transaction relationships
            for tx in transactions:
                if tx.get('from') and tx.get('to'):
                    metadata = {
                        'value': tx.get('value', 0),
                        'gas_price': tx.get('gasPrice', 0),
                        'block_number': tx.get('blockNumber', 0),
                        'timestamp': tx.get('timestamp', 0),
                        'chain_id': tx.get('chainId', 1)
                    }
                    self.neo4j_client.create_transaction_relationship(
                        tx['from'], tx['to'], tx['hash'], metadata
                    )
            
            # Perform entity resolution clustering
            if len(address_transactions) > 1:
                addresses = list(address_transactions.keys())
                clusters = self.resolver.cluster_addresses(addresses, address_transactions)
                
                # Store clusters in Neo4j
                for cluster_id, cluster_addresses in clusters.items():
                    if len(cluster_addresses) > 1:  # Only store clusters with multiple addresses
                        metadata = {
                            'confidence_score': self._calculate_cluster_confidence(cluster_addresses, address_transactions),
                            'cluster_size': len(cluster_addresses),
                            'created_at': datetime.utcnow().isoformat(),
                            'cluster_type': 'behavioral'
                        }
                        self.neo4j_client.create_entity_cluster(cluster_id, cluster_addresses, metadata)
                
                return clusters
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error in entity resolution: {e}")
            return {}
    
    async def process_real_data(self, data_type: str = "latest", limit: int = 100):
        """Process real blockchain data for entity resolution"""
        if not self.real_data_service:
            await self.initialize()
        
        try:
            # Fetch real data based on type
            if data_type == "latest":
                transactions = await self.real_data_service.get_latest_transactions(limit)
            elif data_type == "whale":
                transactions = await self.real_data_service.get_whale_transactions()
            elif data_type == "mev":
                transactions = await self.real_data_service.get_mev_transactions()
            else:
                transactions = await self.real_data_service.get_latest_transactions(limit)
            
            # Process the transactions
            result = await self.process_new_transactions(transactions)
            
            return {
                "status": "success",
                "data_type": data_type,
                "transactions_processed": len(transactions),
                "addresses_found": len(set(tx.get('from') for tx in transactions) | set(tx.get('to') for tx in transactions if tx.get('to'))),
                "clusters_created": len(result),
                "clusters": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing real data: {e}")
            return {
                "error": str(e),
                "transactions_processed": 0,
                "addresses_found": 0,
                "clusters_created": 0,
                "clusters": {}
            }
    
    def _calculate_cluster_confidence(self, addresses: List[str], address_transactions: Dict) -> float:
        """Calculate confidence score for a cluster"""
        if len(addresses) < 2:
            return 0.0
        
        try:
            # Calculate average similarity within cluster
            similarities = []
            for i in range(len(addresses)):
                for j in range(i + 1, len(addresses)):
                    similarity = self.resolver.calculate_similarity_score(
                        addresses[i], 
                        addresses[j], 
                        address_transactions
                    )
                    similarities.append(similarity)
            
            return np.mean(similarities) if similarities else 0.0
        except Exception as e:
            logger.error(f"Error calculating cluster confidence: {e}")
            return 0.0
    
    async def get_entity_info(self, entity_id: str) -> Dict[str, Any]:
        """Get information about a specific entity"""
        try:
            with self.neo4j_client.driver.session() as session:
                query = """
                MATCH (e:Entity {id: $entity_id})-[:OWNS]->(w:Wallet)
                RETURN e, collect(w) as wallets
                """
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                if record:
                    return {
                        'entity_id': record['e']['id'],
                        'metadata': dict(record['e']),
                        'wallets': [w['address'] for w in record['wallets']]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting entity info: {e}")
            return None
    
    async def find_related_entities(self, address: str) -> List[Dict[str, Any]]:
        """Find entities related to a specific address"""
        try:
            with self.neo4j_client.driver.session() as session:
                query = """
                MATCH (w:Wallet {address: $address})-[:OWNS]-(e:Entity)
                MATCH (e)-[:OWNS]->(other_wallets:Wallet)
                RETURN e, collect(other_wallets) as related_wallets
                """
                result = session.run(query, address=address)
                entities = []
                
                for record in result:
                    entities.append({
                        'entity_id': record['e']['id'],
                        'metadata': dict(record['e']),
                        'related_wallets': [w['address'] for w in record['related_wallets']]
                    })
                
                return entities
        except Exception as e:
            logger.error(f"Error finding related entities: {e}")
            return []
    
    async def get_entity_statistics(self) -> Dict[str, Any]:
        """Get statistics about entities and clusters"""
        try:
            with self.neo4j_client.driver.session() as session:
                # Count entities
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()['count']
                
                # Count wallets
                wallet_count = session.run("MATCH (w:Wallet) RETURN count(w) as count").single()['count']
                
                # Count relationships
                relationship_count = session.run("MATCH ()-[r]-() RETURN count(r) as count").single()['count']
                
                # Get cluster distribution
                cluster_sizes = session.run("""
                    MATCH (e:Entity)-[:OWNS]->(w:Wallet)
                    RETURN e.id, count(w) as size
                    ORDER BY size DESC
                    LIMIT 10
                """).data()
                
                return {
                    'total_entities': entity_count,
                    'total_wallets': wallet_count,
                    'total_relationships': relationship_count,
                    'cluster_distribution': cluster_sizes,
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"Error getting entity statistics: {e}")
            return {
                'total_entities': 0,
                'total_wallets': 0,
                'total_relationships': 0,
                'cluster_distribution': [],
                'error': str(e)
            }
