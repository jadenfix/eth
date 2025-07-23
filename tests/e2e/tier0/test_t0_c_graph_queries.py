"""
T0-C: Query Neo4j → returns graph JSON
Demo-blocking test: Basic graph query functionality works
"""

import pytest
import json
from tests.e2e.helpers.neo4j import Neo4jTestUtils

@pytest.mark.e2e
@pytest.mark.tier0
class TestNeo4jGraphQueries:
    """Test basic Neo4j graph query functionality"""
    
    def test_simple_graph_query(self, gcp_env, neo4j_utils, clean_test_data):
        """
        T0-C: Basic Neo4j query test
        
        Flow:
        1. Create test entities and relationships
        2. Query the graph structure
        3. Verify JSON response format
        4. Validate graph data integrity
        """
        # 1. Setup test graph data
        test_entities = [
            {
                "address": "0xT0C123",
                "type": "wallet",
                "risk_score": 0.2,
                "total_volume": 1000000,
                "fixture_id": "T0_C_graph"
            },
            {
                "address": "0xT0C456", 
                "type": "contract",
                "risk_score": 0.1,
                "total_volume": 5000000,
                "fixture_id": "T0_C_graph"
            },
            {
                "address": "0xT0C789",
                "type": "wallet", 
                "risk_score": 0.8,
                "total_volume": 500000,
                "fixture_id": "T0_C_graph"
            }
        ]
        
        test_relationships = [
            {
                "from_address": "0xT0C123",
                "to_address": "0xT0C456",
                "relationship_type": "INTERACTED_WITH",
                "transaction_count": 5,
                "total_value": 2000000,
                "fixture_id": "T0_C_graph"
            },
            {
                "from_address": "0xT0C456",
                "to_address": "0xT0C789", 
                "relationship_type": "SENT_TO",
                "transaction_count": 2,
                "total_value": 1500000,
                "fixture_id": "T0_C_graph"
            }
        ]
        
        # Load test data into Neo4j
        neo4j_utils.load_entities(test_entities)
        neo4j_utils.load_relationships(test_relationships)
        
        # 2. Query graph structure
        query = """
        MATCH (a {fixture_id: 'T0_C_graph'})-[r {fixture_id: 'T0_C_graph'}]->(b {fixture_id: 'T0_C_graph'})
        RETURN a.address as from_addr, 
               a.type as from_type,
               a.risk_score as from_risk,
               r.relationship_type as rel_type,
               r.transaction_count as tx_count,
               b.address as to_addr,
               b.type as to_type,
               b.risk_score as to_risk
        ORDER BY a.address
        """
        
        results = neo4j_utils.query_graph(query)
        
        # 3. Verify JSON response format
        assert isinstance(results, list), "Results should be a list"
        assert len(results) == 2, "Should have 2 relationships"
        
        # 4. Validate graph data integrity
        for result in results:
            assert "from_addr" in result, "Should have from_addr field"
            assert "to_addr" in result, "Should have to_addr field"
            assert "rel_type" in result, "Should have rel_type field"
            assert "tx_count" in result, "Should have tx_count field"
            assert "from_risk" in result, "Should have from_risk field"
            assert "to_risk" in result, "Should have to_risk field"
        
        # Verify specific relationships
        first_rel = results[0]
        assert first_rel["from_addr"] == "0xT0C123"
        assert first_rel["to_addr"] == "0xT0C456"
        assert first_rel["rel_type"] == "INTERACTED_WITH"
        assert first_rel["tx_count"] == 5
        
        second_rel = results[1]
        assert second_rel["from_addr"] == "0xT0C456"
        assert second_rel["to_addr"] == "0xT0C789"
        assert second_rel["rel_type"] == "SENT_TO"
        assert second_rel["tx_count"] == 2
        
        print("✅ T0-C: Basic graph query test passed")
    
    def test_graph_path_query(self, gcp_env, neo4j_utils, clean_test_data):
        """Test graph path queries"""
        # Setup a longer path for testing
        entities = [
            {"address": f"0xPATH{i:03d}", "type": "wallet", "risk_score": 0.1 * i, "fixture_id": "T0_C_path"}
            for i in range(4)
        ]
        
        relationships = [
            {
                "from_address": f"0xPATH{i:03d}",
                "to_address": f"0xPATH{i+1:03d}",
                "relationship_type": "SENT_TO",
                "transaction_count": 1,
                "total_value": 1000000,
                "fixture_id": "T0_C_path"
            }
            for i in range(3)
        ]
        
        neo4j_utils.load_entities(entities)
        neo4j_utils.load_relationships(relationships)
        
        # Query for paths from first to last node
        query = """
        MATCH path = (start {address: '0xPATH000', fixture_id: 'T0_C_path'})
                     -[*1..3 {fixture_id: 'T0_C_path'}]->
                     (end {address: '0xPATH003', fixture_id: 'T0_C_path'})
        RETURN [node in nodes(path) | node.address] as path_addresses,
               length(path) as path_length
        """
        
        results = neo4j_utils.query_graph(query)
        
        assert len(results) == 1, "Should find one path"
        result = results[0]
        assert result["path_length"] == 3, "Path should have length 3"
        assert result["path_addresses"] == ["0xPATH000", "0xPATH001", "0xPATH002", "0xPATH003"]
        
        print("✅ T0-C: Graph path query test passed")
    
    def test_graph_aggregation_query(self, gcp_env, neo4j_utils, clean_test_data):
        """Test graph aggregation queries"""
        # Create a hub node with multiple connections
        hub_entity = {
            "address": "0xHUB001",
            "type": "contract", 
            "risk_score": 0.5,
            "fixture_id": "T0_C_agg"
        }
        
        spoke_entities = [
            {
                "address": f"0xSPOKE{i:02d}",
                "type": "wallet",
                "risk_score": 0.1 * i,
                "fixture_id": "T0_C_agg"
            }
            for i in range(5)
        ]
        
        relationships = [
            {
                "from_address": f"0xSPOKE{i:02d}",
                "to_address": "0xHUB001",
                "relationship_type": "SENT_TO",
                "transaction_count": i + 1,
                "total_value": (i + 1) * 1000000,
                "fixture_id": "T0_C_agg"
            }
            for i in range(5)
        ]
        
        neo4j_utils.load_entities([hub_entity] + spoke_entities)
        neo4j_utils.load_relationships(relationships)
        
        # Query for aggregated data about the hub
        query = """
        MATCH (spoke {fixture_id: 'T0_C_agg'})-[r {fixture_id: 'T0_C_agg'}]->(hub {address: '0xHUB001'})
        RETURN hub.address as hub_address,
               count(spoke) as connected_nodes,
               sum(r.transaction_count) as total_transactions,
               sum(r.total_value) as total_value_received,
               avg(spoke.risk_score) as avg_spoke_risk
        """
        
        results = neo4j_utils.query_graph(query)
        
        assert len(results) == 1, "Should have one aggregated result"
        result = results[0]
        
        assert result["hub_address"] == "0xHUB001"
        assert result["connected_nodes"] == 5
        assert result["total_transactions"] == 15  # 1+2+3+4+5
        assert result["total_value_received"] == 15000000  # 1M+2M+3M+4M+5M
        assert abs(result["avg_spoke_risk"] - 0.2) < 0.01  # (0+0.1+0.2+0.3+0.4)/5
        
        print("✅ T0-C: Graph aggregation query test passed")
    
    def test_graph_export_format(self, gcp_env, neo4j_utils, clean_test_data):
        """Test graph data export in proper JSON format"""
        # Create simple test graph
        entities = [
            {"address": "0xEXPORT1", "type": "wallet", "label": "User Wallet", "fixture_id": "T0_C_export"},
            {"address": "0xEXPORT2", "type": "contract", "label": "DeFi Protocol", "fixture_id": "T0_C_export"}
        ]
        
        relationships = [
            {
                "from_address": "0xEXPORT1",
                "to_address": "0xEXPORT2", 
                "relationship_type": "INTERACTED_WITH",
                "weight": 0.8,
                "fixture_id": "T0_C_export"
            }
        ]
        
        neo4j_utils.load_entities(entities)
        neo4j_utils.load_relationships(relationships)
        
        # Export graph data
        export_data = neo4j_utils.export_graph_data("fixture_id = 'T0_C_export'")
        
        # Validate export format
        assert "nodes" in export_data, "Export should have 'nodes' field"
        assert "edges" in export_data, "Export should have 'edges' field"
        
        # Validate nodes format
        nodes = export_data["nodes"]
        assert len(nodes) == 2, "Should have 2 nodes"
        for node in nodes:
            assert "id" in node, "Node should have 'id' field"
            assert "type" in node, "Node should have 'type' field"
            assert "properties" in node, "Node should have 'properties' field"
        
        # Validate edges format
        edges = export_data["edges"]
        assert len(edges) == 1, "Should have 1 edge"
        edge = edges[0]
        assert "source" in edge, "Edge should have 'source' field"
        assert "target" in edge, "Edge should have 'target' field"
        assert "type" in edge, "Edge should have 'type' field"
        assert "properties" in edge, "Edge should have 'properties' field"
        
        # Verify JSON serialization
        json_str = json.dumps(export_data)
        recovered_data = json.loads(json_str)
        assert recovered_data == export_data, "Should be JSON serializable"
        
        print("✅ T0-C: Graph export format test passed")
