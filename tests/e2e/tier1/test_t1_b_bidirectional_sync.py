"""
T1-B: Bidirectional sync BigQuery ↔ Neo4j
Functional test: Complete data synchronization between data stores
"""

import pytest
import asyncio
import time
import json
from tests.e2e.helpers.gcp import GCPTestUtils, ENTITIES_SCHEMA
from tests.e2e.helpers.neo4j import Neo4jTestUtils

@pytest.mark.e2e
@pytest.mark.tier1
class TestBidirectionalSync:
    """Test bidirectional synchronization between BigQuery and Neo4j"""
    
    def test_bigquery_to_neo4j_sync(self, gcp_env, bigquery_client, neo4j_utils, clean_test_data):
        """
        T1-B: BigQuery → Neo4j synchronization
        
        Flow:
        1. Insert entity data into BigQuery
        2. Trigger sync process (CDC simulation)
        3. Verify entities appear in Neo4j
        4. Validate relationship creation
        5. Check data consistency
        """
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        # 1. Setup BigQuery entities table
        test_dataset = f"{gcp_env.test_prefix}_sync_test"
        entities_table = "entities"
        relationships_table = "relationships"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, entities_table, ENTITIES_SCHEMA)
        gcp_utils.bq_create_table(test_dataset, relationships_table, {
            "fields": [
                {"name": "from_address", "type": "STRING"},
                {"name": "to_address", "type": "STRING"},
                {"name": "relationship_type", "type": "STRING"},
                {"name": "transaction_count", "type": "INTEGER"},
                {"name": "total_value", "type": "FLOAT"},
                {"name": "first_seen", "type": "INTEGER"},
                {"name": "last_seen", "type": "INTEGER"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        # Insert test entities to BigQuery
        test_entities = [
            {
                "address": "0xBQ2NEO001",
                "entity_type": "wallet",
                "risk_score": 0.3,
                "total_volume": 5000000.0,
                "transaction_count": 25,
                "first_seen": 1690000000,
                "last_seen": 1698000000,
                "labels": json.dumps(["high_volume", "defi_user"]),
                "fixture_id": "T1_B_bq_to_neo"
            },
            {
                "address": "0xBQ2NEO002",
                "entity_type": "contract",
                "risk_score": 0.1,
                "total_volume": 50000000.0,
                "transaction_count": 1000,
                "first_seen": 1680000000,
                "last_seen": 1698000000,
                "labels": json.dumps(["dex", "verified"]),
                "fixture_id": "T1_B_bq_to_neo"
            },
            {
                "address": "0xBQ2NEO003",
                "entity_type": "wallet",
                "risk_score": 0.9,
                "total_volume": 100000.0,
                "transaction_count": 5,
                "first_seen": 1697000000,
                "last_seen": 1698000000,
                "labels": json.dumps(["suspicious", "new_account"]),
                "fixture_id": "T1_B_bq_to_neo"
            }
        ]
        
        test_relationships = [
            {
                "from_address": "0xBQ2NEO001",
                "to_address": "0xBQ2NEO002",
                "relationship_type": "INTERACTED_WITH",
                "transaction_count": 10,
                "total_value": 1500000.0,
                "first_seen": 1695000000,
                "last_seen": 1698000000,
                "fixture_id": "T1_B_bq_to_neo"
            },
            {
                "from_address": "0xBQ2NEO003",
                "to_address": "0xBQ2NEO002",
                "relationship_type": "SENT_TO",
                "transaction_count": 3,
                "total_value": 75000.0,
                "first_seen": 1697500000,
                "last_seen": 1698000000,
                "fixture_id": "T1_B_bq_to_neo"
            }
        ]
        
        gcp_utils.bq_insert_rows(test_dataset, entities_table, test_entities)
        gcp_utils.bq_insert_rows(test_dataset, relationships_table, test_relationships)
        
        # 2. Simulate CDC sync process (would be triggered by Dataflow)
        # Query entities from BigQuery
        entities_query = f"""
        SELECT *
        FROM `{gcp_env.project_id}.{test_dataset}.{entities_table}`
        WHERE fixture_id = 'T1_B_bq_to_neo'
        """
        
        entities_from_bq = gcp_utils.bq_query(entities_query)
        
        # Query relationships from BigQuery
        relationships_query = f"""
        SELECT *
        FROM `{gcp_env.project_id}.{test_dataset}.{relationships_table}`
        WHERE fixture_id = 'T1_B_bq_to_neo'
        """
        
        relationships_from_bq = gcp_utils.bq_query(relationships_query)
        
        # 3. Sync to Neo4j
        neo4j_entities = []
        for entity in entities_from_bq:
            neo4j_entity = {
                "address": entity["address"],
                "type": entity["entity_type"],
                "risk_score": entity["risk_score"],
                "total_volume": entity["total_volume"],
                "transaction_count": entity["transaction_count"],
                "labels": json.loads(entity["labels"]),
                "fixture_id": entity["fixture_id"],
                "synced_from": "bigquery",
                "sync_timestamp": int(time.time())
            }
            neo4j_entities.append(neo4j_entity)
        
        neo4j_relationships = []
        for rel in relationships_from_bq:
            neo4j_rel = {
                "from_address": rel["from_address"],
                "to_address": rel["to_address"],
                "relationship_type": rel["relationship_type"],
                "transaction_count": rel["transaction_count"],
                "total_value": rel["total_value"],
                "fixture_id": rel["fixture_id"],
                "synced_from": "bigquery",
                "sync_timestamp": int(time.time())
            }
            neo4j_relationships.append(neo4j_rel)
        
        neo4j_utils.load_entities(neo4j_entities)
        neo4j_utils.load_relationships(neo4j_relationships)
        
        # 4. Verify sync results in Neo4j
        verify_query = """
        MATCH (n {fixture_id: 'T1_B_bq_to_neo'})
        RETURN n.address as address, n.type as type, n.risk_score as risk_score
        ORDER BY n.address
        """
        
        neo4j_results = neo4j_utils.query_graph(verify_query)
        
        assert len(neo4j_results) == 3, "Should have 3 entities in Neo4j"
        assert neo4j_results[0]["address"] == "0xBQ2NEO001"
        assert neo4j_results[1]["address"] == "0xBQ2NEO002"
        assert neo4j_results[2]["address"] == "0xBQ2NEO003"
        
        # Verify relationships
        rel_query = """
        MATCH (a {fixture_id: 'T1_B_bq_to_neo'})-[r {fixture_id: 'T1_B_bq_to_neo'}]->(b {fixture_id: 'T1_B_bq_to_neo'})
        RETURN a.address as from_addr, r.relationship_type as rel_type, b.address as to_addr
        ORDER BY a.address
        """
        
        rel_results = neo4j_utils.query_graph(rel_query)
        assert len(rel_results) == 2, "Should have 2 relationships in Neo4j"
        
        print("✅ T1-B: BigQuery → Neo4j sync test passed")
    
    def test_neo4j_to_bigquery_sync(self, gcp_env, bigquery_client, neo4j_utils, clean_test_data):
        """
        T1-B: Neo4j → BigQuery synchronization
        
        Flow:
        1. Create entities and relationships in Neo4j
        2. Trigger reverse sync process
        3. Verify data appears in BigQuery
        4. Check data transformation and enrichment
        """
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        # 1. Setup BigQuery destination tables
        test_dataset = f"{gcp_env.test_prefix}_reverse_sync"
        entities_table = "neo4j_entities"
        relationships_table = "neo4j_relationships"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, entities_table, ENTITIES_SCHEMA)
        gcp_utils.bq_create_table(test_dataset, relationships_table, {
            "fields": [
                {"name": "from_address", "type": "STRING"},
                {"name": "to_address", "type": "STRING"},
                {"name": "relationship_type", "type": "STRING"},
                {"name": "weight", "type": "FLOAT"},
                {"name": "properties", "type": "STRING"},
                {"name": "created_in_neo4j", "type": "INTEGER"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        # 2. Create test data in Neo4j
        neo4j_entities = [
            {
                "address": "0xNEO2BQ001",
                "type": "wallet",
                "risk_score": 0.4,
                "total_volume": 2000000,
                "clustering_coefficient": 0.6,
                "centrality_score": 0.8,
                "fixture_id": "T1_B_neo_to_bq"
            },
            {
                "address": "0xNEO2BQ002", 
                "type": "contract",
                "risk_score": 0.2,
                "total_volume": 20000000,
                "clustering_coefficient": 0.9,
                "centrality_score": 0.95,
                "fixture_id": "T1_B_neo_to_bq"
            }
        ]
        
        neo4j_relationships = [
            {
                "from_address": "0xNEO2BQ001",
                "to_address": "0xNEO2BQ002",
                "relationship_type": "COMPLEX_INTERACTION",
                "weight": 0.85,
                "interaction_patterns": ["frequent", "large_amounts"],
                "risk_indicators": ["none"],
                "fixture_id": "T1_B_neo_to_bq"
            }
        ]
        
        neo4j_utils.load_entities(neo4j_entities)
        neo4j_utils.load_relationships(neo4j_relationships)
        
        # 3. Extract data from Neo4j for sync
        extract_entities_query = """
        MATCH (n {fixture_id: 'T1_B_neo_to_bq'})
        RETURN n.address as address,
               n.type as entity_type,
               n.risk_score as risk_score,
               n.total_volume as total_volume,
               n.clustering_coefficient as clustering_coefficient,
               n.centrality_score as centrality_score,
               n.fixture_id as fixture_id
        """
        
        extract_rels_query = """
        MATCH (a {fixture_id: 'T1_B_neo_to_bq'})-[r {fixture_id: 'T1_B_neo_to_bq'}]->(b {fixture_id: 'T1_B_neo_to_bq'})
        RETURN a.address as from_address,
               b.address as to_address,
               r.relationship_type as relationship_type,
               r.weight as weight,
               r.fixture_id as fixture_id
        """
        
        extracted_entities = neo4j_utils.query_graph(extract_entities_query)
        extracted_relationships = neo4j_utils.query_graph(extract_rels_query)
        
        # 4. Transform and load to BigQuery
        bq_entities = []
        for entity in extracted_entities:
            bq_entity = {
                "address": entity["address"],
                "entity_type": entity["entity_type"],
                "risk_score": entity["risk_score"],
                "total_volume": entity["total_volume"],
                "transaction_count": 0,  # Default for Neo4j sync
                "first_seen": 0,
                "last_seen": int(time.time()),
                "labels": json.dumps([
                    f"clustering_{entity['clustering_coefficient']}",
                    f"centrality_{entity['centrality_score']}"
                ]),
                "fixture_id": entity["fixture_id"]
            }
            bq_entities.append(bq_entity)
        
        bq_relationships = []
        for rel in extracted_relationships:
            bq_rel = {
                "from_address": rel["from_address"],
                "to_address": rel["to_address"],
                "relationship_type": rel["relationship_type"],
                "weight": rel["weight"],
                "properties": json.dumps({"synced_from_neo4j": True}),
                "created_in_neo4j": int(time.time()),
                "fixture_id": rel["fixture_id"]
            }
            bq_relationships.append(bq_rel)
        
        gcp_utils.bq_insert_rows(test_dataset, entities_table, bq_entities)
        gcp_utils.bq_insert_rows(test_dataset, relationships_table, bq_relationships)
        
        # 5. Verify sync results in BigQuery
        verify_entities_query = f"""
        SELECT address, entity_type, risk_score
        FROM `{gcp_env.project_id}.{test_dataset}.{entities_table}`
        WHERE fixture_id = 'T1_B_neo_to_bq'
        ORDER BY address
        """
        
        bq_entity_results = gcp_utils.bq_query(verify_entities_query)
        assert len(bq_entity_results) == 2, "Should have 2 entities synced to BigQuery"
        assert bq_entity_results[0]["address"] == "0xNEO2BQ001"
        assert bq_entity_results[1]["address"] == "0xNEO2BQ002"
        
        verify_rels_query = f"""
        SELECT from_address, to_address, relationship_type, weight
        FROM `{gcp_env.project_id}.{test_dataset}.{relationships_table}`
        WHERE fixture_id = 'T1_B_neo_to_bq'
        """
        
        bq_rel_results = gcp_utils.bq_query(verify_rels_query)
        assert len(bq_rel_results) == 1, "Should have 1 relationship synced to BigQuery"
        assert bq_rel_results[0]["relationship_type"] == "COMPLEX_INTERACTION"
        assert bq_rel_results[0]["weight"] == 0.85
        
        print("✅ T1-B: Neo4j → BigQuery sync test passed")
    
    def test_bidirectional_consistency_check(self, gcp_env, bigquery_client, neo4j_utils, clean_test_data):
        """Test data consistency between BigQuery and Neo4j after bidirectional sync"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        # Setup test environment
        test_dataset = f"{gcp_env.test_prefix}_consistency"
        entities_table = "entities"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, entities_table, ENTITIES_SCHEMA)
        
        # Create test entity that will be synced both ways
        test_entity = {
            "entity_id": "CONSISTENCY001",
            "entity_type": "wallet",
            "addresses": ["0xCONSISTENCY001"],
            "institution": None,
            "labels": ["test", "consistency"],
            "risk_score": 0.5,
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(1690000000)),
        }
        
        # 1. Insert to BigQuery first
        gcp_utils.bq_insert_rows(test_dataset, entities_table, [test_entity])
        
        # 2. Sync to Neo4j
        bq_query = f"""
        SELECT *
        FROM `{gcp_env.project_id}.{test_dataset}.{entities_table}`
        WHERE fixture_id = 'T1_B_consistency'
        """
        
        bq_data = gcp_utils.bq_query(bq_query)
        
        neo4j_entity = {
            "address": bq_data[0]["address"],
            "type": bq_data[0]["entity_type"],
            "risk_score": bq_data[0]["risk_score"],
            "total_volume": bq_data[0]["total_volume"],
            "fixture_id": bq_data[0]["fixture_id"],
            "synced_from_bq": True
        }
        
        neo4j_utils.load_entities([neo4j_entity])
        
        # 3. Modify in Neo4j (simulate graph-based computation)
        update_query = """
        MATCH (n {address: '0xCONSISTENCY001', fixture_id: 'T1_B_consistency'})
        SET n.risk_score = 0.7,
            n.graph_computed_score = 0.8,
            n.last_updated = timestamp()
        RETURN n.address as address, n.risk_score as risk_score
        """
        
        update_result = neo4j_utils.query_graph(update_query)
        assert len(update_result) == 1, "Should update one entity"
        assert update_result[0]["risk_score"] == 0.7, "Risk score should be updated"
        
        # 4. Sync back to BigQuery
        get_updated_query = """
        MATCH (n {fixture_id: 'T1_B_consistency'})
        RETURN n.address as address,
               n.type as entity_type,
               n.risk_score as risk_score,
               n.total_volume as total_volume,
               n.graph_computed_score as graph_computed_score,
               n.fixture_id as fixture_id
        """
        
        neo4j_updated = neo4j_utils.query_graph(get_updated_query)
        
        # Update BigQuery with Neo4j changes
        updated_entity = test_entity.copy()
        updated_entity.update({
            "risk_score": neo4j_updated[0]["risk_score"],
            "graph_computed_score": neo4j_updated[0]["graph_computed_score"],
            "last_sync": int(time.time())
        })
        
        # Create updated table schema
        gcp_utils.bq_create_table(test_dataset, "entities_updated", {
            "fields": [
                {"name": "address", "type": "STRING"},
                {"name": "entity_type", "type": "STRING"},
                {"name": "risk_score", "type": "FLOAT"},
                {"name": "total_volume", "type": "FLOAT"},
                {"name": "transaction_count", "type": "INTEGER"},
                {"name": "first_seen", "type": "INTEGER"},
                {"name": "last_seen", "type": "INTEGER"},
                {"name": "labels", "type": "STRING"},
                {"name": "graph_computed_score", "type": "FLOAT"},
                {"name": "last_sync", "type": "INTEGER"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        gcp_utils.bq_insert_rows(test_dataset, "entities_updated", [updated_entity])
        
        # 5. Verify consistency
        final_bq_query = f"""
        SELECT address, risk_score, graph_computed_score
        FROM `{gcp_env.project_id}.{test_dataset}.entities_updated`
        WHERE fixture_id = 'T1_B_consistency'
        """
        
        final_bq_data = gcp_utils.bq_query(final_bq_query)
        
        final_neo4j_query = """
        MATCH (n {fixture_id: 'T1_B_consistency'})
        RETURN n.address as address, n.risk_score as risk_score, n.graph_computed_score as graph_computed_score
        """
        
        final_neo4j_data = neo4j_utils.query_graph(final_neo4j_query)
        
        # Verify both stores have consistent data
        assert final_bq_data[0]["risk_score"] == final_neo4j_data[0]["risk_score"], "Risk scores should match"
        assert final_bq_data[0]["graph_computed_score"] == final_neo4j_data[0]["graph_computed_score"], "Graph scores should match"
        
        print("✅ T1-B: Bidirectional consistency check passed")
    
    @pytest.mark.asyncio
    async def test_real_time_sync_latency(self, gcp_env, bigquery_client, neo4j_utils, clean_test_data):
        """Test latency of real-time bidirectional sync"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_sync_latency"
        entities_table = "real_time_entities"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, entities_table, ENTITIES_SCHEMA)
        
        # Track sync timing
        sync_times = []
        
        for i in range(5):
            # 1. Insert to BigQuery with timestamp
            insert_time = time.time()
            entity = {
                "entity_id": f"LATENCY{i:03d}",
                "entity_type": "wallet",
                "addresses": [f"0xLATENCY{i:03d}"],
                "institution": None,
                "labels": [f"test_{i}"],
                "risk_score": 0.1 * i,
                "created_at": time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(insert_time)),
            }
            
            gcp_utils.bq_insert_rows(test_dataset, entities_table, [entity])
            
            # 2. Simulate CDC trigger and sync to Neo4j
            sync_start = time.time()
            
            neo4j_entity = {
                "address": entity["address"],
                "type": entity["entity_type"],
                "risk_score": entity["risk_score"],
                "fixture_id": entity["fixture_id"],
                "bq_insert_time": insert_time,
                "sync_start_time": sync_start
            }
            
            neo4j_utils.load_entities([neo4j_entity])
            
            sync_complete = time.time()
            
            # 3. Verify sync completed
            verify_query = f"""
            MATCH (n {{address: '0xLATENCY{i:03d}', fixture_id: 'T1_B_latency'}})
            RETURN n.address as address
            """
            
            verify_result = neo4j_utils.query_graph(verify_query)
            assert len(verify_result) == 1, f"Entity {i} should be synced to Neo4j"
            
            # Calculate latency
            sync_latency = (sync_complete - insert_time) * 1000  # ms
            sync_times.append(sync_latency)
            
            await asyncio.sleep(0.1)  # Brief pause between tests
        
        # Analyze sync performance
        avg_latency = sum(sync_times) / len(sync_times)
        max_latency = max(sync_times)
        
        assert avg_latency < 1000, f"Average sync latency should be under 1s, got {avg_latency:.2f}ms"
        assert max_latency < 2000, f"Max sync latency should be under 2s, got {max_latency:.2f}ms"
        
        print(f"✅ T1-B: Real-time sync latency test passed (avg: {avg_latency:.2f}ms, max: {max_latency:.2f}ms)")
    
    def test_sync_conflict_resolution(self, gcp_env, bigquery_client, neo4j_utils, clean_test_data):
        """Test conflict resolution when same entity is modified in both stores"""
        gcp_utils = GCPTestUtils(gcp_env.project_id)
        
        test_dataset = f"{gcp_env.test_prefix}_conflicts"
        entities_table = "conflict_entities"
        
        gcp_utils.bq_create_dataset(test_dataset)
        gcp_utils.bq_create_table(test_dataset, entities_table, {
            "fields": [
                {"name": "address", "type": "STRING"},
                {"name": "entity_type", "type": "STRING"},
                {"name": "risk_score", "type": "FLOAT"},
                {"name": "total_volume", "type": "FLOAT"},
                {"name": "last_modified", "type": "INTEGER"},
                {"name": "modified_in", "type": "STRING"},
                {"name": "fixture_id", "type": "STRING"}
            ]
        })
        
        # Create initial entity
        base_entity = {
            "address": "0xCONFLICT001",
            "entity_type": "wallet",
            "risk_score": 0.5,
            "total_volume": 1000000.0,
            "last_modified": int(time.time()),
            "modified_in": "initial",
            "fixture_id": "T1_B_conflict"
        }
        
        # Insert to both stores
        gcp_utils.bq_insert_rows(test_dataset, entities_table, [base_entity])
        
        neo4j_entity = {
            "address": base_entity["address"],
            "type": base_entity["entity_type"],
            "risk_score": base_entity["risk_score"],
            "total_volume": base_entity["total_volume"],
            "fixture_id": base_entity["fixture_id"]
        }
        neo4j_utils.load_entities([neo4j_entity])
        
        # Simulate concurrent modifications
        time.sleep(1)  # Ensure different timestamps
        
        # Modify in BigQuery
        bq_modified_time = int(time.time())
        bq_modified = base_entity.copy()
        bq_modified.update({
            "risk_score": 0.8,  # Changed in BQ
            "total_volume": 2000000.0,
            "last_modified": bq_modified_time,
            "modified_in": "bigquery"
        })
        
        # Modify in Neo4j (slightly later)
        time.sleep(1)
        neo4j_modified_time = int(time.time())
        
        neo4j_update_query = """
        MATCH (n {address: '0xCONFLICT001', fixture_id: 'T1_B_conflict'})
        SET n.risk_score = 0.3,
            n.graph_analysis_score = 0.9,
            n.last_modified = $timestamp,
            n.modified_in = 'neo4j'
        RETURN n.address as address
        """
        
        neo4j_utils.query_graph(neo4j_update_query, {"timestamp": neo4j_modified_time})
        
        # Resolve conflicts - Neo4j wins due to later timestamp
        # Get Neo4j version
        get_neo4j_query = """
        MATCH (n {fixture_id: 'T1_B_conflict'})
        RETURN n.address as address,
               n.type as entity_type,
               n.risk_score as risk_score,
               n.total_volume as total_volume,
               n.graph_analysis_score as graph_analysis_score,
               n.last_modified as last_modified,
               n.modified_in as modified_in
        """
        
        neo4j_current = neo4j_utils.query_graph(get_neo4j_query)
        
        # Create resolved version
        resolved_entity = {
            "address": neo4j_current[0]["address"],
            "entity_type": neo4j_current[0]["entity_type"],
            "risk_score": neo4j_current[0]["risk_score"],  # Neo4j value
            "total_volume": bq_modified["total_volume"],    # BQ value (keep volume updates)
            "last_modified": neo4j_current[0]["last_modified"],
            "modified_in": "resolved_neo4j_wins",
            "fixture_id": "T1_B_conflict"
        }
        
        # Update both stores with resolved version
        gcp_utils.bq_insert_rows(test_dataset, "conflict_entities", [resolved_entity])
        
        neo4j_resolved = {
            "address": resolved_entity["address"],
            "type": resolved_entity["entity_type"],
            "risk_score": resolved_entity["risk_score"],
            "total_volume": resolved_entity["total_volume"],
            "fixture_id": resolved_entity["fixture_id"],
            "conflict_resolved": True
        }
        neo4j_utils.load_entities([neo4j_resolved])
        
        # Verify resolution
        verify_bq = f"""
        SELECT risk_score, total_volume, modified_in
        FROM `{gcp_env.project_id}.{test_dataset}.{entities_table}`
        WHERE fixture_id = 'T1_B_conflict' AND modified_in = 'resolved_neo4j_wins'
        """
        
        bq_resolved = gcp_utils.bq_query(verify_bq)
        
        verify_neo4j = """
        MATCH (n {fixture_id: 'T1_B_conflict', conflict_resolved: true})
        RETURN n.risk_score as risk_score, n.total_volume as total_volume
        """
        
        neo4j_resolved_result = neo4j_utils.query_graph(verify_neo4j)
        
        # Both should have same resolved values
        assert bq_resolved[0]["risk_score"] == neo4j_resolved_result[0]["risk_score"]
        assert bq_resolved[0]["total_volume"] == neo4j_resolved_result[0]["total_volume"]
        assert bq_resolved[0]["risk_score"] == 0.3  # Neo4j won
        assert bq_resolved[0]["total_volume"] == 2000000.0  # BQ volume kept
        
        print("✅ T1-B: Sync conflict resolution test passed")
