# Phase 2: Entity Resolution & Graph Database Implementation Guide

## 🎯 **PHASE 2 OVERVIEW**


MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 
MAKE SURE THIS WORKS WITH WHAT WE HAVE ALREADY AND DO END TO END TESTS WHEN COMPLETE 

**Goal:** Build the semantic fusion layer for entity clustering and relationship mapping

**Duration:** 2 Weeks (Week 3: Neo4j Integration, Week 4: GraphQL API & Ontology)

**Prerequisites:** ✅ Phase 1 completed (Authentication, Multi-chain data)
**Target Status:** 🕸️ Entity resolution pipeline + Graph database with relationships

---

## 📋 **WEEK 3: NEO4J INTEGRATION**

### **Day 1-2: Neo4j AuraDB Setup**

#### **Step 1: Set Up Neo4j AuraDB Instance**
```bash
# Install Neo4j Python driver
cd /Users/jadenfix/eth
pip install neo4j python-dotenv

env variables are in the .env file 

#### **Step 2: Create Neo4j Client**
**File:** `services/graph_api/neo4j_client.py`

```python
import os
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
    
    def close(self):
        self.driver.close()
    
    def create_wallet_node(self, address: str, metadata: Dict[str, Any] = None):
        """Create a wallet node in Neo4j"""
        with self.driver.session() as session:
            query = """
            MERGE (w:Wallet {address: $address})
            SET w += $metadata
            RETURN w
            """
            result = session.run(query, address=address, metadata=metadata or {})
            return result.single()
    
    def create_transaction_relationship(
        self, 
        from_address: str, 
        to_address: str, 
        tx_hash: str,
        metadata: Dict[str, Any] = None
    ):
        """Create a transaction relationship between wallets"""
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
    
    def create_entity_cluster(self, entity_id: str, addresses: List[str], metadata: Dict[str, Any] = None):
        """Create an entity cluster with multiple addresses"""
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
```

### **Day 3-4: Entity Resolution Algorithms**

#### **Step 1: Create Entity Resolution Service**
**File:** `services/entity_resolution/entity_resolver.py`

```python
import hashlib
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer

class EntityResolver:
    def __init__(self):
        self.address_clusters = defaultdict(list)
        self.entity_counter = 0
    
    def extract_features(self, address: str, transactions: List[Dict]) -> Dict[str, Any]:
        """Extract features from address and its transactions"""
        features = {
            'address': address,
            'transaction_count': len(transactions),
            'total_value_sent': sum(tx.get('value', 0) for tx in transactions),
            'total_value_received': sum(tx.get('value', 0) for tx in transactions if tx.get('to') == address),
            'unique_contracts': len(set(tx.get('to') for tx in transactions if tx.get('input') != '0x')),
            'avg_gas_price': np.mean([tx.get('gasPrice', 0) for tx in transactions]),
            'activity_pattern': self._extract_activity_pattern(transactions),
            'time_between_txs': self._calculate_time_intervals(transactions)
        }
        return features
    
    def _extract_activity_pattern(self, transactions: List[Dict]) -> str:
        """Extract activity pattern as a string for similarity comparison"""
        patterns = []
        for tx in transactions:
            if tx.get('input') == '0x':
                patterns.append('transfer')
            elif tx.get('to') in ['0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D']:  # Uniswap
                patterns.append('swap')
            else:
                patterns.append('contract')
        return ' '.join(patterns)
    
    def _calculate_time_intervals(self, transactions: List[Dict]) -> List[float]:
        """Calculate time intervals between transactions"""
        timestamps = sorted([tx.get('timestamp', 0) for tx in transactions])
        intervals = []
        for i in range(1, len(timestamps)):
            intervals.append(timestamps[i] - timestamps[i-1])
        return intervals
    
    def cluster_addresses(self, addresses_data: Dict[str, List[Dict]]) -> Dict[str, List[str]]:
        """Cluster addresses based on behavioral similarity"""
        # Extract features for all addresses
        features_list = []
        address_list = []
        
        for address, transactions in addresses_data.items():
            features = self.extract_features(address, transactions)
            features_list.append(features)
            address_list.append(address)
        
        # Create feature matrix for clustering
        feature_matrix = []
        for features in features_list:
            feature_vector = [
                features['transaction_count'],
                features['total_value_sent'],
                features['total_value_received'],
                features['unique_contracts'],
                features['avg_gas_price']
            ]
            feature_matrix.append(feature_vector)
        
        # Normalize features
        feature_matrix = np.array(feature_matrix)
        feature_matrix = (feature_matrix - feature_matrix.mean(axis=0)) / feature_matrix.std(axis=0)
        
        # Perform clustering
        clustering = DBSCAN(eps=0.5, min_samples=2).fit(feature_matrix)
        
        # Group addresses by cluster
        clusters = defaultdict(list)
        for address, cluster_id in zip(address_list, clustering.labels_):
            if cluster_id != -1:  # Not noise
                clusters[f"entity_{cluster_id}"].append(address)
        
        return dict(clusters)
    
    def calculate_similarity_score(self, addr1_features: Dict, addr2_features: Dict) -> float:
        """Calculate similarity score between two addresses"""
        # Simple cosine similarity for numerical features
        features1 = np.array([
            addr1_features['transaction_count'],
            addr1_features['total_value_sent'],
            addr1_features['total_value_received'],
            addr1_features['unique_contracts'],
            addr1_features['avg_gas_price']
        ])
        
        features2 = np.array([
            addr2_features['transaction_count'],
            addr2_features['total_value_sent'],
            addr2_features['total_value_received'],
            addr2_features['unique_contracts'],
            addr2_features['avg_gas_price']
        ])
        
        # Normalize
        features1 = features1 / (np.linalg.norm(features1) + 1e-8)
        features2 = features2 / (np.linalg.norm(features2) + 1e-8)
        
        similarity = np.dot(features1, features2)
        
        # Add pattern similarity
        pattern_similarity = self._calculate_pattern_similarity(
            addr1_features['activity_pattern'],
            addr2_features['activity_pattern']
        )
        
        return 0.7 * similarity + 0.3 * pattern_similarity
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """Calculate similarity between activity patterns"""
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([pattern1, pattern2])
            similarity = (tfidf_matrix * tfidf_matrix.T).A[0, 1]
            return similarity
        except:
            return 0.0
```

#### **Step 2: Create Entity Resolution Pipeline**
**File:** `services/entity_resolution/pipeline.py`

```python
import asyncio
from typing import Dict, List, Any
from .entity_resolver import EntityResolver
from ..graph_api.neo4j_client import Neo4jClient
from ..ethereum_ingester.ethereum_ingester import EthereumIngester

class EntityResolutionPipeline:
    def __init__(self):
        self.resolver = EntityResolver()
        self.neo4j_client = Neo4jClient()
        self.ingester = EthereumIngester()
    
    async def process_new_transactions(self, transactions: List[Dict[str, Any]]):
        """Process new transactions for entity resolution"""
        # Group transactions by address
        address_transactions = defaultdict(list)
        for tx in transactions:
            address_transactions[tx['from']].append(tx)
            if tx.get('to'):
                address_transactions[tx['to']].append(tx)
        
        # Perform entity resolution
        clusters = self.resolver.cluster_addresses(address_transactions)
        
        # Store results in Neo4j
        for entity_id, addresses in clusters.items():
            if len(addresses) > 1:  # Only store clusters with multiple addresses
                metadata = {
                    'confidence_score': self._calculate_cluster_confidence(addresses, address_transactions),
                    'cluster_size': len(addresses),
                    'created_at': datetime.utcnow().isoformat()
                }
                
                self.neo4j_client.create_entity_cluster(entity_id, addresses, metadata)
        
        return clusters
    
    def _calculate_cluster_confidence(self, addresses: List[str], address_transactions: Dict) -> float:
        """Calculate confidence score for a cluster"""
        if len(addresses) < 2:
            return 0.0
        
        # Calculate average similarity within cluster
        similarities = []
        for i in range(len(addresses)):
            for j in range(i + 1, len(addresses)):
                addr1_features = self.resolver.extract_features(
                    addresses[i], 
                    address_transactions[addresses[i]]
                )
                addr2_features = self.resolver.extract_features(
                    addresses[j], 
                    address_transactions[addresses[j]]
                )
                similarity = self.resolver.calculate_similarity_score(addr1_features, addr2_features)
                similarities.append(similarity)
        
        return np.mean(similarities) if similarities else 0.0
    
    async def get_entity_info(self, entity_id: str) -> Dict[str, Any]:
        """Get information about a specific entity"""
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
    
    async def find_related_entities(self, address: str) -> List[Dict[str, Any]]:
        """Find entities related to a specific address"""
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
```

### **Day 5-7: Wallet Clustering Logic**

#### **Step 1: Create Advanced Clustering Service**
**File:** `services/entity_resolution/advanced_clustering.py`

```python
import networkx as nx
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class AdvancedWalletClustering:
    def __init__(self):
        self.graph = nx.Graph()
        self.clusters = defaultdict(set)
        self.similarity_threshold = 0.7
    
    def build_transaction_graph(self, transactions: List[Dict[str, Any]]):
        """Build a graph from transaction data"""
        for tx in transactions:
            from_addr = tx.get('from')
            to_addr = tx.get('to')
            
            if from_addr and to_addr:
                # Add nodes
                self.graph.add_node(from_addr)
                self.graph.add_node(to_addr)
                
                # Add edge with weight based on transaction value
                weight = min(tx.get('value', 0) / 1e18, 1.0)  # Normalize to 0-1
                self.graph.add_edge(from_addr, to_addr, weight=weight)
    
    def detect_exchange_clusters(self, transactions: List[Dict]) -> List[Set[str]]:
        """Detect exchange-like wallet clusters"""
        exchange_patterns = {
            'high_frequency': 100,  # transactions per day
            'low_value': 0.1,  # ETH
            'contract_interaction': 0.8  # % of contract interactions
        }
        
        # Group transactions by address
        addr_stats = defaultdict(lambda: {
            'tx_count': 0,
            'total_value': 0,
            'contract_txs': 0
        })
        
        for tx in transactions:
            addr = tx.get('from')
            if addr:
                addr_stats[addr]['tx_count'] += 1
                addr_stats[addr]['total_value'] += tx.get('value', 0) / 1e18
                if tx.get('input') != '0x':
                    addr_stats[addr]['contract_txs'] += 1
        
        # Identify exchange-like addresses
        exchange_addresses = set()
        for addr, stats in addr_stats.items():
            if (stats['tx_count'] > exchange_patterns['high_frequency'] and
                stats['total_value'] < exchange_patterns['low_value'] and
                stats['contract_txs'] / stats['tx_count'] > exchange_patterns['contract_interaction']):
                exchange_addresses.add(addr)
        
        # Cluster exchange addresses
        return self._cluster_addresses(exchange_addresses)
    
    def detect_whale_clusters(self, transactions: List[Dict]) -> List[Set[str]]:
        """Detect whale wallet clusters"""
        whale_threshold = 100  # ETH
        
        # Find high-value transactions
        whale_addresses = set()
        for tx in transactions:
            value_eth = tx.get('value', 0) / 1e18
            if value_eth > whale_threshold:
                whale_addresses.add(tx.get('from'))
                whale_addresses.add(tx.get('to'))
        
        return self._cluster_addresses(whale_addresses)
    
    def detect_mev_bot_clusters(self, transactions: List[Dict]) -> List[Set[str]]:
        """Detect MEV bot clusters"""
        mev_patterns = {
            'high_gas': 200,  # gwei
            'flash_loan': True,
            'sandwich_pattern': True
        }
        
        mev_addresses = set()
        for tx in transactions:
            gas_price_gwei = tx.get('gasPrice', 0) / 1e9
            if gas_price_gwei > mev_patterns['high_gas']:
                mev_addresses.add(tx.get('from'))
        
        return self._cluster_addresses(mev_addresses)
    
    def _cluster_addresses(self, addresses: Set[str]) -> List[Set[str]]:
        """Cluster addresses based on transaction patterns"""
        if not addresses:
            return []
        
        # Create subgraph for these addresses
        subgraph = self.graph.subgraph(addresses)
        
        # Find connected components
        clusters = []
        for component in nx.connected_components(subgraph):
            if len(component) > 1:  # Only clusters with multiple addresses
                clusters.append(component)
        
        return clusters
    
    def calculate_cluster_metrics(self, cluster: Set[str]) -> Dict[str, Any]:
        """Calculate metrics for a wallet cluster"""
        subgraph = self.graph.subgraph(cluster)
        
        return {
            'size': len(cluster),
            'density': nx.density(subgraph),
            'average_clustering': nx.average_clustering(subgraph),
            'centrality': nx.degree_centrality(subgraph),
            'betweenness': nx.betweenness_centrality(subgraph)
        }
```

---

## 📋 **WEEK 4: GRAPHQL API & ONTOLOGY**

### **Day 1-3: GraphQL API Development**

#### **Step 1: Create GraphQL Schema**
**File:** `services/graph_api/schema.graphql`

```graphql
type Wallet {
  id: ID!
  address: String!
  entity: Entity
  transactions: [Transaction!]!
  balance: Float
  firstSeen: String
  lastSeen: String
  metadata: JSON
}

type Entity {
  id: ID!
  wallets: [Wallet!]!
  confidence: Float
  entityType: String
  labels: [String!]
  metadata: JSON
  createdAt: String
  updatedAt: String
}

type Transaction {
  id: ID!
  hash: String!
  from: Wallet!
  to: Wallet!
  value: Float!
  gasPrice: Float!
  gasUsed: Int!
  blockNumber: Int!
  timestamp: String!
  status: Boolean!
  chainId: Int!
  metadata: JSON
}

type Cluster {
  id: ID!
  addresses: [String!]!
  confidence: Float!
  clusterType: String!
  metrics: ClusterMetrics!
  createdAt: String!
}

type ClusterMetrics {
  size: Int!
  density: Float!
  averageClustering: Float!
  centrality: JSON!
  betweenness: JSON!
}

type Query {
  wallet(address: String!): Wallet
  entity(id: String!): Entity
  transaction(hash: String!): Transaction
  cluster(id: String!): Cluster
  
  wallets(
    limit: Int = 10
    offset: Int = 0
    entityType: String
    minBalance: Float
  ): [Wallet!]!
  
  entities(
    limit: Int = 10
    offset: Int = 0
    entityType: String
    minConfidence: Float
  ): [Entity!]!
  
  transactions(
    limit: Int = 10
    offset: Int = 0
    fromAddress: String
    toAddress: String
    minValue: Float
    chainId: Int
  ): [Transaction!]!
  
  clusters(
    limit: Int = 10
    offset: Int = 0
    clusterType: String
    minConfidence: Float
  ): [Cluster!]!
  
  searchEntities(query: String!, limit: Int = 10): [Entity!]!
  getRelatedEntities(address: String!): [Entity!]!
}

type Mutation {
  createEntity(input: CreateEntityInput!): Entity!
  updateEntity(id: String!, input: UpdateEntityInput!): Entity!
  deleteEntity(id: String!): Boolean!
  
  createCluster(input: CreateClusterInput!): Cluster!
  updateCluster(id: String!, input: UpdateClusterInput!): Cluster!
  deleteCluster(id: String!): Boolean!
}

input CreateEntityInput {
  wallets: [String!]!
  entityType: String
  labels: [String!]
  metadata: JSON
}

input UpdateEntityInput {
  wallets: [String!]
  entityType: String
  labels: [String!]
  metadata: JSON
}

input CreateClusterInput {
  addresses: [String!]!
  clusterType: String!
  confidence: Float!
  metrics: JSON
}

input UpdateClusterInput {
  addresses: [String!]
  clusterType: String
  confidence: Float
  metrics: JSON
}

scalar JSON
```

#### **Step 2: Create GraphQL Resolvers**
**File:** `services/graph_api/resolvers.py`

```python
from typing import List, Dict, Any, Optional
from .neo4j_client import Neo4jClient
from .entity_resolution.pipeline import EntityResolutionPipeline

class GraphQLResolvers:
    def __init__(self):
        self.neo4j_client = Neo4jClient()
        self.entity_pipeline = EntityResolutionPipeline()
    
    async def resolve_wallet(self, address: str) -> Optional[Dict[str, Any]]:
        """Resolve wallet by address"""
        with self.neo4j_client.driver.session() as session:
            query = """
            MATCH (w:Wallet {address: $address})
            OPTIONAL MATCH (w)-[:OWNS]-(e:Entity)
            RETURN w, e
            """
            result = session.run(query, address=address)
            record = result.single()
            
            if record:
                return {
                    'id': record['w']['address'],
                    'address': record['w']['address'],
                    'entity': record['e'] if record['e'] else None,
                    'metadata': dict(record['w'])
                }
            return None
    
    async def resolve_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Resolve entity by ID"""
        with self.neo4j_client.driver.session() as session:
            query = """
            MATCH (e:Entity {id: $entity_id})-[:OWNS]->(w:Wallet)
            RETURN e, collect(w) as wallets
            """
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            
            if record:
                return {
                    'id': record['e']['id'],
                    'wallets': [{'address': w['address']} for w in record['wallets']],
                    'confidence': record['e'].get('confidence_score', 0.0),
                    'entityType': record['e'].get('entity_type'),
                    'labels': record['e'].get('labels', []),
                    'metadata': dict(record['e']),
                    'createdAt': record['e'].get('created_at'),
                    'updatedAt': record['e'].get('updated_at')
                }
            return None
    
    async def resolve_entities(
        self, 
        limit: int = 10, 
        offset: int = 0,
        entity_type: Optional[str] = None,
        min_confidence: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Resolve multiple entities with filtering"""
        with self.neo4j_client.driver.session() as session:
            query = """
            MATCH (e:Entity)
            """
            
            conditions = []
            params = {'limit': limit, 'offset': offset}
            
            if entity_type:
                conditions.append("e.entity_type = $entity_type")
                params['entity_type'] = entity_type
            
            if min_confidence:
                conditions.append("e.confidence_score >= $min_confidence")
                params['min_confidence'] = min_confidence
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += """
            RETURN e
            ORDER BY e.confidence_score DESC
            SKIP $offset
            LIMIT $limit
            """
            
            result = session.run(query, **params)
            entities = []
            
            for record in result:
                entities.append({
                    'id': record['e']['id'],
                    'confidence': record['e'].get('confidence_score', 0.0),
                    'entityType': record['e'].get('entity_type'),
                    'labels': record['e'].get('labels', []),
                    'metadata': dict(record['e'])
                })
            
            return entities
    
    async def resolve_search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search entities by query"""
        with self.neo4j_client.driver.session() as session:
            # Search by address, entity ID, or labels
            search_query = """
            MATCH (e:Entity)
            WHERE e.id CONTAINS $query
               OR e.labels CONTAINS $query
               OR EXISTS((e)-[:OWNS]->(w:Wallet WHERE w.address CONTAINS $query))
            RETURN e
            LIMIT $limit
            """
            
            result = session.run(search_query, query=query, limit=limit)
            entities = []
            
            for record in result:
                entities.append({
                    'id': record['e']['id'],
                    'confidence': record['e'].get('confidence_score', 0.0),
                    'entityType': record['e'].get('entity_type'),
                    'labels': record['e'].get('labels', []),
                    'metadata': dict(record['e'])
                })
            
            return entities
    
    async def resolve_related_entities(self, address: str) -> List[Dict[str, Any]]:
        """Find entities related to an address"""
        return await self.entity_pipeline.find_related_entities(address)
```

#### **Step 3: Create GraphQL Server**
**File:** `services/graph_api/graphql_server.py`

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry
from typing import List, Optional
from .resolvers import GraphQLResolvers
from .schema import schema

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

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "graph-api"}

# Add metrics endpoint
@app.get("/metrics")
async def get_metrics():
    resolvers = GraphQLResolvers()
    
    # Get basic metrics
    with resolvers.neo4j_client.driver.session() as session:
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
        "uptime": "running"
    }
```

### **Day 4-5: Relationship Mapping**

#### **Step 1: Create Relationship Mapper**
**File:** `services/graph_api/relationship_mapper.py`

```python
from typing import Dict, List, Any, Set
from collections import defaultdict
import networkx as nx

class RelationshipMapper:
    def __init__(self):
        self.neo4j_client = Neo4jClient()
        self.relationship_types = {
            'TRANSACTED_WITH': 'transaction',
            'OWNS': 'ownership',
            'SIMILAR_TO': 'similarity',
            'COLLABORATES_WITH': 'collaboration'
        }
    
    def map_transaction_relationships(self, transactions: List[Dict[str, Any]]):
        """Map transaction relationships between addresses"""
        for tx in transactions:
            from_addr = tx.get('from')
            to_addr = tx.get('to')
            
            if from_addr and to_addr:
                metadata = {
                    'tx_hash': tx.get('hash'),
                    'value': tx.get('value'),
                    'gas_price': tx.get('gasPrice'),
                    'block_number': tx.get('blockNumber'),
                    'timestamp': tx.get('timestamp'),
                    'chain_id': tx.get('chainId', 1)
                }
                
                self.neo4j_client.create_transaction_relationship(
                    from_addr, to_addr, tx.get('hash'), metadata
                )
    
    def map_ownership_relationships(self, entity_clusters: Dict[str, List[str]]):
        """Map ownership relationships for entity clusters"""
        for entity_id, addresses in entity_clusters.items():
            self.neo4j_client.create_entity_cluster(entity_id, addresses)
    
    def map_similarity_relationships(self, address_features: Dict[str, Dict]):
        """Map similarity relationships between addresses"""
        addresses = list(address_features.keys())
        
        for i in range(len(addresses)):
            for j in range(i + 1, len(addresses)):
                addr1, addr2 = addresses[i], addresses[j]
                
                similarity = self._calculate_similarity(
                    address_features[addr1],
                    address_features[addr2]
                )
                
                if similarity > 0.8:  # High similarity threshold
                    with self.neo4j_client.driver.session() as session:
                        query = """
                        MATCH (w1:Wallet {address: $addr1})
                        MATCH (w2:Wallet {address: $addr2})
                        MERGE (w1)-[r:SIMILAR_TO]->(w2)
                        SET r.similarity_score = $similarity
                        RETURN r
                        """
                        session.run(query, addr1=addr1, addr2=addr2, similarity=similarity)
    
    def map_collaboration_relationships(self, transactions: List[Dict[str, Any]]):
        """Map collaboration relationships based on transaction patterns"""
        # Group transactions by time windows
        time_windows = defaultdict(list)
        for tx in transactions:
            timestamp = tx.get('timestamp', 0)
            window = timestamp // 3600  # 1-hour windows
            time_windows[window].append(tx)
        
        # Find addresses that frequently interact in the same time windows
        address_interactions = defaultdict(set)
        for window, window_txs in time_windows.items():
            addresses = set()
            for tx in window_txs:
                addresses.add(tx.get('from'))
                addresses.add(tx.get('to'))
            
            # Create collaboration relationships
            addr_list = list(addresses)
            for i in range(len(addr_list)):
                for j in range(i + 1, len(addr_list)):
                    address_interactions[addr_list[i]].add(addr_list[j])
                    address_interactions[addr_list[j]].add(addr_list[i])
        
        # Create collaboration relationships in Neo4j
        for addr1, collaborators in address_interactions.items():
            for addr2 in collaborators:
                if len(collaborators) > 2:  # Only if they have multiple collaborators
                    with self.neo4j_client.driver.session() as session:
                        query = """
                        MATCH (w1:Wallet {address: $addr1})
                        MATCH (w2:Wallet {address: $addr2})
                        MERGE (w1)-[r:COLLABORATES_WITH]->(w2)
                        SET r.collaboration_strength = $strength
                        RETURN r
                        """
                        strength = len(collaborators) / 10.0  # Normalize
                        session.run(query, addr1=addr1, addr2=addr2, strength=strength)
    
    def _calculate_similarity(self, features1: Dict, features2: Dict) -> float:
        """Calculate similarity between two address feature sets"""
        # Simple cosine similarity
        keys = set(features1.keys()) & set(features2.keys())
        if not keys:
            return 0.0
        
        dot_product = sum(features1[k] * features2[k] for k in keys)
        norm1 = sum(features1[k] ** 2 for k in keys) ** 0.5
        norm2 = sum(features2[k] ** 2 for k in keys) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_relationship_graph(self, address: str, depth: int = 2) -> Dict[str, Any]:
        """Get relationship graph for an address"""
        with self.neo4j_client.driver.session() as session:
            query = """
            MATCH path = (start:Wallet {address: $address})-[*1..$depth]-(related)
            RETURN path
            """
            result = session.run(query, address=address, depth=depth)
            
            nodes = set()
            edges = []
            
            for record in result:
                path = record['path']
                for node in path.nodes:
                    nodes.add((node['address'], dict(node)))
                for rel in path.relationships:
                    edges.append({
                        'from': rel.start_node['address'],
                        'to': rel.end_node['address'],
                        'type': rel.type,
                        'properties': dict(rel)
                    })
            
            return {
                'nodes': list(nodes),
                'edges': edges
            }
```

### **Day 6-7: Entity Confidence Scoring**

#### **Step 1: Create Confidence Scoring System**
**File:** `services/entity_resolution/confidence_scorer.py`

```python
import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class ConfidenceScorer:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_names = [
            'transaction_count',
            'total_value_sent',
            'total_value_received',
            'unique_contracts',
            'avg_gas_price',
            'time_span',
            'address_count',
            'similarity_score'
        ]
    
    def extract_confidence_features(self, entity_data: Dict[str, Any]) -> List[float]:
        """Extract features for confidence scoring"""
        features = []
        
        # Transaction-based features
        features.append(entity_data.get('transaction_count', 0))
        features.append(entity_data.get('total_value_sent', 0))
        features.append(entity_data.get('total_value_received', 0))
        features.append(entity_data.get('unique_contracts', 0))
        features.append(entity_data.get('avg_gas_price', 0))
        
        # Time-based features
        features.append(entity_data.get('time_span', 0))
        
        # Cluster-based features
        features.append(entity_data.get('address_count', 1))
        features.append(entity_data.get('similarity_score', 0))
        
        return features
    
    def calculate_confidence_score(self, entity_data: Dict[str, Any]) -> float:
        """Calculate confidence score for an entity"""
        features = self.extract_confidence_features(entity_data)
        
        # Rule-based scoring
        score = 0.0
        
        # Address count bonus
        address_count = entity_data.get('address_count', 1)
        if address_count > 1:
            score += min(address_count * 0.1, 0.3)
        
        # Transaction volume bonus
        total_value = entity_data.get('total_value_sent', 0) + entity_data.get('total_value_received', 0)
        if total_value > 1000:  # High value entity
            score += 0.2
        
        # Contract interaction bonus
        contract_ratio = entity_data.get('unique_contracts', 0) / max(entity_data.get('transaction_count', 1), 1)
        if contract_ratio > 0.5:
            score += 0.15
        
        # Similarity score bonus
        similarity = entity_data.get('similarity_score', 0)
        score += similarity * 0.3
        
        # Time span bonus
        time_span = entity_data.get('time_span', 0)
        if time_span > 86400 * 30:  # More than 30 days
            score += 0.1
        
        return min(score, 1.0)
    
    def train_confidence_model(self, training_data: List[Dict[str, Any]]):
        """Train the confidence scoring model"""
        X = []
        y = []
        
        for entity in training_data:
            features = self.extract_confidence_features(entity)
            X.append(features)
            y.append(entity.get('is_valid_entity', 0))
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        return accuracy
    
    def predict_confidence(self, entity_data: Dict[str, Any]) -> float:
        """Predict confidence using trained model"""
        features = self.extract_confidence_features(entity_data)
        prediction = self.model.predict_proba([features])[0]
        return prediction[1]  # Probability of being a valid entity
    
    def update_entity_confidence(self, entity_id: str, neo4j_client):
        """Update confidence score for an entity in Neo4j"""
        with neo4j_client.driver.session() as session:
            # Get entity data
            query = """
            MATCH (e:Entity {id: $entity_id})-[:OWNS]->(w:Wallet)
            RETURN e, collect(w) as wallets
            """
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            
            if record:
                entity_data = dict(record['e'])
                entity_data['address_count'] = len(record['wallets'])
                
                # Calculate new confidence score
                confidence = self.calculate_confidence_score(entity_data)
                
                # Update in Neo4j
                update_query = """
                MATCH (e:Entity {id: $entity_id})
                SET e.confidence_score = $confidence,
                    e.updated_at = datetime()
                RETURN e
                """
                session.run(update_query, entity_id=entity_id, confidence=confidence)
                
                return confidence
        
        return 0.0
```

---

## 🚀 **IMPLEMENTATION CHECKLIST**

### **Week 3 Checklist:**
- [ ] Set up Neo4j AuraDB instance
- [ ] Create Neo4j client with basic operations
- [ ] Implement entity resolution algorithms
- [ ] Create wallet clustering logic
- [ ] Test entity resolution pipeline
- [ ] Verify Neo4j data storage

### **Week 4 Checklist:**
- [ ] Create GraphQL schema
- [ ] Implement GraphQL resolvers
- [ ] Set up GraphQL server
- [ ] Create relationship mapping system
- [ ] Implement confidence scoring
- [ ] Test GraphQL API endpoints

---

## 🧪 **TESTING STRATEGY**

### **Entity Resolution Tests:**
```python
# Test entity clustering
from services.entity_resolution.pipeline import EntityResolutionPipeline

pipeline = EntityResolutionPipeline()
clusters = await pipeline.process_new_transactions(sample_transactions)
print(f"Found {len(clusters)} entity clusters")
```

### **GraphQL API Tests:**
```bash
# Test GraphQL endpoint
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ entities(limit: 5) { id confidence entityType } }"}'

# Test entity search
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ searchEntities(query: \"0x123\") { id wallets { address } } }"}'
```

### **Neo4j Tests:**
```python
# Test Neo4j connection
from services.graph_api.neo4j_client import Neo4jClient

client = Neo4jClient()
result = client.create_wallet_node("0x123", {"label": "test"})
print(f"Created wallet: {result}")
```

---

## 📊 **SUCCESS METRICS**

### **Week 3 Success Criteria:**
- ✅ Neo4j AuraDB connected and operational
- ✅ Entity resolution algorithms working
- ✅ Wallet clustering producing results
- ✅ Data being stored in Neo4j

### **Week 4 Success Criteria:**
- ✅ GraphQL API responding to queries
- ✅ Relationship mapping functional
- ✅ Confidence scoring working
- ✅ Entity search operational

---

## 🔧 **TROUBLESHOOTING**

### **Common Issues:**

1. **Neo4j connection failing:**
   - Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD environment variables
   - Verify AuraDB instance is running
   - Check network connectivity

2. **Entity resolution not working:**
   - Verify transaction data format
   - Check clustering parameters
   - Monitor algorithm performance

3. **GraphQL API errors:**
   - Check schema syntax
   - Verify resolver implementations
   - Test individual resolvers

### **Debug Commands:**
```bash
# Test Neo4j connection
python -c "from services.graph_api.neo4j_client import Neo4jClient; Neo4jClient().driver.verify_connectivity()"

# Test entity resolution
python -c "from services.entity_resolution.pipeline import EntityResolutionPipeline; print('Pipeline ready')"

# Test GraphQL server
curl http://localhost:4000/health
```

---

## 📈 **NEXT STEPS**

After completing Phase 2, you'll have:
- ✅ Entity resolution pipeline
- ✅ Graph database with relationships
- ✅ GraphQL API for queries
- ✅ Wallet clustering algorithms
- ✅ Confidence scoring system

**Ready for Phase 3:** Intelligence Agents (MEV detection, risk scoring, sanctions screening)

This foundation enables advanced compliance features and intelligence gathering. 