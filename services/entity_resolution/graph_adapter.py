"""Actual Neo4j entity adapter with no ML/cloud imports."""

import asyncio
import json
import os
from datetime import datetime, timezone
from neo4j import GraphDatabase


class GraphUpdater:
    def __init__(self, driver=None, driver_factory=None):
        self.driver = driver
        self.driver_factory = driver_factory or GraphDatabase.driver

    async def update_entity_graph(self, entity_data):
        identity = entity_data.get("entity_id")
        addresses = entity_data.get("addresses")
        confidence = float(entity_data.get("confidence", 0))
        if (
            not identity
            or not isinstance(addresses, list)
            or not addresses
            or not 0 <= confidence <= 1
        ):
            raise ValueError("Invalid entity graph candidate")
        if self.driver is None:
            self.driver = self.driver_factory(
                os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
                auth=(
                    os.getenv("NEO4J_USER", "neo4j"),
                    os.getenv("NEO4J_PASSWORD", ""),
                ),
            )

        def update():
            with self.driver.session() as session:
                previous = session.run(
                    "MATCH (e:Entity {id:$id}) RETURN e.payload AS payload", id=identity
                ).single()
                previous_payload = previous.get("payload") if previous else None
                old = (
                    json.loads(previous_payload)
                    if isinstance(previous_payload, str)
                    else {}
                )
                created = (
                    old.get("createdAt")
                    or entity_data.get("createdAt")
                    or datetime.now(timezone.utc).isoformat()
                )
                return session.run(
                    "MERGE (e:Entity {id:$id}) SET e.type=$type,e.confidence=$confidence,e.addresses=$addresses,e.resolution_method=$method,e.payload=$payload,e.labels=$labels,e.riskScore=$risk WITH e UNWIND $addresses AS address MERGE (a:Address {address:address}) MERGE (e)-[:HAS_ADDRESS]->(a) RETURN e",
                    id=identity,
                    type=entity_data.get("entity_type", "UNKNOWN"),
                    confidence=confidence,
                    method=entity_data.get("resolution_method", "behavioral_candidate"),
                    addresses=addresses,
                    payload=json.dumps(
                        {
                            "id": identity,
                            "type": entity_data.get("entity_type", "UNKNOWN"),
                            "addresses": addresses,
                            "confidence": confidence,
                            "labels": entity_data.get("labels", []),
                            "riskScore": None,
                            "createdAt": created,
                            "updatedAt": datetime.now(timezone.utc).isoformat(),
                        },
                        allow_nan=False,
                    ),
                    labels=entity_data.get("labels", []),
                    risk=None,
                ).consume()

        await asyncio.to_thread(update)
        return entity_data

    def close(self):
        if self.driver:
            self.driver.close()
