"""Actual storage, HTTP GraphQL, permissions, restart and provider boundaries."""

import os
import sqlite3
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from services.graph_api.store import GraphStore
from services.graph_api.graph_api import create_app


def execute(client, query, variables=None, token="graph-test-token"):
    return client.post(
        "/graphql",
        json={"query": query, "variables": variables},
        headers={"Authorization": f"Bearer {token}"},
    )


def workflow(store):
    client = TestClient(create_app(store, token="graph-test-token"))
    create = "mutation($input:EntityInput!){createEntity(input:$input){id type addresses confidence riskScore}}"
    first = execute(
        client,
        create,
        {
            "input": {
                "id": "ROOT_A",
                "type": "EXCHANGE",
                "addresses": ["0xa"],
                "confidence": 0.8,
                "riskScore": 0,
            }
        },
    ).json()
    assert not first.get("errors"), first
    assert first["data"]["createEntity"]["addresses"] == ["0xa"]
    second = execute(
        client, create, {"input": {"id": "ROOT_B", "type": "ADDRESS", "riskScore": 10}}
    ).json()
    assert not second.get("errors"), second
    denied = execute(client, create, {"input": {"type": "PERSON"}}, token="invalid")
    assert denied.status_code == 403
    edge = execute(
        client,
        'mutation{createRelationship(input:{type:"TRANSACTED_WITH",fromEntityId:"ROOT_A",toEntityId:"ROOT_B",weight:0.5}){id relationship_type}}',
    ).json()
    assert not edge.get("errors"), edge
    network = execute(
        client,
        '{getEntityNetwork(id:"ROOT_A",depth:1){nodes{id} edges{from_entity to_entity} depth}}',
    ).json()
    assert {node["id"] for node in network["data"]["getEntityNetwork"]["nodes"]} == {
        "ROOT_A",
        "ROOT_B",
    }
    zero = execute(client, "{entities(filter:{riskScoreMax:0}){id}}").json()
    assert zero["data"]["entities"] == [{"id": "ROOT_A"}]
    empty = execute(client, "{entities(filter:{hasAddress:false}){id}}").json()
    assert empty["data"]["entities"] == [{"id": "ROOT_B"}]
    assert execute(client, "{entities(limit:0){id}}").json().get("errors")
    assert (
        execute(client, '{getEntityNetwork(id:"ROOT_A",depth:500){depth}}')
        .json()
        .get("errors")
    )
    assert execute(client, "not graphql").status_code == 400
    assert (
        execute(
            client,
            'mutation{createRelationship(input:{type:"OWNS",fromEntityId:"ROOT_A",toEntityId:"MISSING"}){id}}',
        )
        .json()
        .get("errors")
    )
    updated = execute(
        client,
        'mutation{updateEntity(id:"ROOT_A",input:{riskScore:5,name:"actual update"}){riskScore name}}',
    ).json()
    assert updated["data"]["updateEntity"]["riskScore"] == 5
    client.close()


def test_sqlite_graphql_roundtrip_and_restart(tmp_path):
    path = tmp_path / "graph.sqlite"
    store = GraphStore(path=path, uri="")
    workflow(store)
    store.close()
    restored = GraphStore(path=path, uri="")
    assert restored.get_entity("ROOT_A")["name"] == "actual update"
    assert restored.get_relationships("ROOT_A")[0]["to_entity"] == "ROOT_B"
    assert len(restored.get_entities()) == 2
    assert len(restored.get_entity_network("ROOT_A", 1)["edges"]) == 1


def test_validated_inputs_and_atomic_missing_endpoints(tmp_path):
    store = GraphStore(path=tmp_path / "graph.sqlite", uri="")
    store.create_entity({"id": "a", "type": "ADDRESS"})
    with pytest.raises(sqlite3.IntegrityError):
        store.create_relationship({"from_entity": "a", "to_entity": "missing"})
    assert store.get_relationships("a") == []
    for data in [
        {"labels": "not a list"},
        {"addresses": None},
        {"confidence": float("nan")},
        {"riskScore": -1},
    ]:
        with pytest.raises((ValueError, TypeError)):
            store.create_entity({"id": "bad", "type": "PERSON", **data})
    assert store.get_entity("bad") is None


def test_missing_provider_is_visible_not_healthy(tmp_path):
    store = GraphStore(path=tmp_path / "graph.sqlite", uri="")
    with patch.object(
        store, "get_entities", side_effect=RuntimeError("provider unavailable")
    ):
        client = TestClient(create_app(store))
        response = execute(client, "{entities{id}}").json()
        assert response["data"] is None and response["errors"]


def test_real_neo4j_workflow():
    if os.getenv("GRAPH_REQUIRE_NEO4J") != "1":
        pytest.skip("opt-in actual Neo4j server; mandatory in graph service CI")
    uri = os.environ["NEO4J_URI"]
    store = GraphStore(uri=uri)
    store.driver.verify_connectivity()
    with store.driver.session() as session:
        session.run(
            "MATCH (e:Entity) WHERE e.id IN $ids DETACH DELETE e",
            ids=["ROOT_A", "ROOT_B"],
        ).consume()
    workflow(store)
    store.close()
    restored = GraphStore(uri=uri)
    assert restored.get_entity("ROOT_A")["name"] == "actual update"
    assert restored.get_relationships("ROOT_A")[0]["to_entity"] == "ROOT_B"
    restored.close()
