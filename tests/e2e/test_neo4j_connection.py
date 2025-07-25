import os
import pytest
from neo4j import GraphDatabase, basic_auth

@pytest.mark.neo4j
def test_neo4j_connection():
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    assert uri and user and password, "NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set in the environment"
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            value = result.single()["test"]
            assert value == 1, "Neo4j connection test failed: unexpected return value"
    finally:
        driver.close() 