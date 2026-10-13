"""Durable local graph and an explicit Neo4j adapter; no synthetic records."""

import json
import math
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path


def limit_value(value=100):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
        raise ValueError("limit must be an integer from 1 to 1000")
    return value


def entity_record(data):
    item = dict(data)
    item["id"] = str(item.get("id") or uuid.uuid4())
    item["type"] = str(item.get("type", "ADDRESS"))
    addresses = item.get("addresses", [])
    if not isinstance(addresses, list) or any(
        not isinstance(a, str) for a in addresses
    ):
        raise ValueError("addresses must be a list of strings")
    if item.get("address") and item["address"] not in addresses:
        addresses = [*addresses, item["address"]]
    item["addresses"] = list(dict.fromkeys(addresses))
    item["labels"] = item.get("labels", [])
    if not isinstance(item["labels"], list) or any(
        not isinstance(label, str) for label in item["labels"]
    ):
        raise ValueError("labels must be a list of strings")
    for field, low, high in [("confidence", 0, 1), ("riskScore", 0, 100)]:
        raw = item.get(field, 0 if field == "confidence" else None)
        if raw is None and field == "riskScore":
            item[field] = None
            continue
        value = float(raw)
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f"invalid {field}")
        item[field] = value
    now = datetime.now(timezone.utc).isoformat()
    item.setdefault("createdAt", now)
    item["updatedAt"] = now
    return item


class GraphStore:
    def __init__(self, *, path=None, uri=None, user=None, password=None):
        self.uri = uri if uri is not None else os.getenv("NEO4J_URI")
        self.mode = "neo4j" if self.uri else "sqlite"
        self.driver = None
        self.path = str(path or os.getenv("GRAPH_DB_PATH", "./data/ontology.sqlite"))
        if self.uri:
            from neo4j import GraphDatabase

            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(
                    user or os.getenv("NEO4J_USER", "neo4j"),
                    password or os.getenv("NEO4J_PASSWORD"),
                ),
                connection_timeout=5,
                max_transaction_retry_time=5,
            )
            with self.driver.session() as session:
                session.run(
                    "CREATE CONSTRAINT ontology_entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE"
                ).consume()
                session.run(
                    "CREATE CONSTRAINT ontology_relationship_id IF NOT EXISTS FOR ()-[r:RELATIONSHIP]-() REQUIRE r.id IS UNIQUE"
                ).consume()
        else:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            with self.db() as db:
                db.executescript(
                    "PRAGMA foreign_keys=ON; CREATE TABLE IF NOT EXISTS entities(id TEXT PRIMARY KEY, payload TEXT NOT NULL); CREATE TABLE IF NOT EXISTS relationships(id TEXT PRIMARY KEY, source TEXT NOT NULL REFERENCES entities(id), target TEXT NOT NULL REFERENCES entities(id), payload TEXT NOT NULL);"
                )

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.path, timeout=5)
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def close(self):
        if self.driver:
            self.driver.close()

    def _records(self, statement, **params):
        with self.driver.session() as session:
            return [record.data() for record in session.run(statement, **params)]

    def create_entity(self, data):
        item = entity_record(data)
        payload = json.dumps(item, allow_nan=False)
        if self.driver:
            records = self._records(
                "CREATE (e:Entity {id:$id, type:$type, addresses:$addresses, confidence:$confidence, riskScore:$risk, labels:$labels, payload:$payload}) RETURN e.payload AS payload",
                id=item["id"],
                type=item["type"],
                addresses=item["addresses"],
                confidence=item["confidence"],
                risk=item["riskScore"],
                labels=item["labels"],
                payload=payload,
            )
            if not records:
                raise RuntimeError("Neo4j did not commit the entity")
        else:
            with self.db() as db:
                db.execute(
                    "INSERT INTO entities(id,payload) VALUES(?,?)",
                    (item["id"], payload),
                )
        return item

    def get_entity(self, entity_id):
        if self.driver:
            rows = self._records(
                "MATCH (e:Entity {id:$id}) RETURN e.payload AS payload", id=entity_id
            )
            return json.loads(rows[0]["payload"]) if rows else None
        with self.db() as db:
            row = db.execute(
                "SELECT payload FROM entities WHERE id=?", (entity_id,)
            ).fetchone()
        return json.loads(row[0]) if row else None

    def get_entities(self, filters=None, limit=100):
        limit = limit_value(limit)
        filters = filters or {}
        if self.driver:
            rows = self._records(
                "MATCH (e:Entity) WHERE ($type IS NULL OR e.type=$type) AND ($labels IS NULL OR any(label IN $labels WHERE label IN e.labels)) AND ($hasAddress IS NULL OR (size(e.addresses)>0)=$hasAddress) AND ($minimum IS NULL OR e.riskScore >= $minimum) AND ($maximum IS NULL OR e.riskScore <= $maximum) RETURN e.payload AS payload ORDER BY e.id LIMIT $limit",
                type=filters.get("type"),
                labels=filters.get("labels") or None,
                hasAddress=filters.get("hasAddress"),
                minimum=filters.get("riskScoreMin"),
                maximum=filters.get("riskScoreMax"),
                limit=limit,
            )
            items = [json.loads(row["payload"]) for row in rows]
        else:
            with self.db() as db:
                items = [
                    json.loads(row[0])
                    for row in db.execute("SELECT payload FROM entities ORDER BY id")
                ]
        for key in ["riskScoreMin", "riskScoreMax"]:
            if filters.get(key) is not None and not math.isfinite(float(filters[key])):
                raise ValueError("risk filter must be finite")
        return [
            item
            for item in items
            if (not filters.get("type") or item["type"] == filters["type"])
            and (
                not filters.get("labels")
                or any(label in item["labels"] for label in filters["labels"])
            )
            and (
                filters.get("hasAddress") is None
                or bool(item["addresses"]) == filters["hasAddress"]
            )
            and (
                filters.get("riskScoreMin") is None
                or (
                    item["riskScore"] is not None
                    and item["riskScore"] >= filters["riskScoreMin"]
                )
            )
            and (
                filters.get("riskScoreMax") is None
                or (
                    item["riskScore"] is not None
                    and item["riskScore"] <= filters["riskScoreMax"]
                )
            )
        ][:limit]

    def update_entity(self, entity_id, changes):
        current = self.get_entity(entity_id)
        if current is None:
            raise ValueError("entity does not exist")
        allowed = {
            "name",
            "labels",
            "properties",
            "riskScore",
            "confidence",
            "addresses",
        }
        if set(changes) - allowed:
            raise ValueError("immutable or unknown entity field")
        item = entity_record({**current, **changes})
        payload = json.dumps(item, allow_nan=False)
        if self.driver:
            self._records(
                "MATCH (e:Entity {id:$id}) SET e.payload=$payload, e.addresses=$addresses, e.confidence=$confidence, e.riskScore=$risk, e.labels=$labels RETURN e.id AS id",
                id=entity_id,
                payload=payload,
                addresses=item["addresses"],
                confidence=item["confidence"],
                risk=item["riskScore"],
                labels=item["labels"],
            )
        else:
            with self.db() as db:
                db.execute(
                    "UPDATE entities SET payload=? WHERE id=?", (payload, entity_id)
                )
        return item

    def create_relationship(self, data):
        source = data.get("fromEntityId") or data.get("from_entity")
        target = data.get("toEntityId") or data.get("to_entity")
        if not source or not target:
            raise ValueError("both relationship endpoints are required")
        item = {
            **data,
            "id": str(data.get("id") or uuid.uuid4()),
            "from_entity": source,
            "to_entity": target,
            "relationship_type": data.get("type")
            or data.get("relationship_type", "RELATED_TO"),
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        payload = json.dumps(item, allow_nan=False)
        if self.driver:
            rows = self._records(
                "MATCH (a:Entity {id:$source}), (b:Entity {id:$target}) CREATE (a)-[r:RELATIONSHIP {id:$id, type:$type, payload:$payload}]->(b) RETURN r.id AS id",
                source=source,
                target=target,
                id=item["id"],
                type=item["relationship_type"],
                payload=payload,
            )
            if not rows:
                raise ValueError("relationship endpoint does not exist")
        else:
            with self.db() as db:
                db.execute(
                    "INSERT INTO relationships(id,source,target,payload) VALUES(?,?,?,?)",
                    (item["id"], source, target, payload),
                )
        return item

    def get_relationships(
        self, entity_id=None, limit=100, target=None, relationship_type=None
    ):
        limit = limit_value(limit)
        if self.driver:
            rows = self._records(
                "MATCH (a:Entity)-[r:RELATIONSHIP]->(b:Entity) WHERE ($id IS NULL OR a.id=$id OR b.id=$id) RETURN r.payload AS payload ORDER BY r.id LIMIT $limit",
                id=entity_id,
                limit=1000,
            )
            items = [json.loads(row["payload"]) for row in rows]
        else:
            with self.db() as db:
                rows = db.execute(
                    "SELECT payload FROM relationships WHERE (? IS NULL OR source=? OR target=?) ORDER BY id",
                    (entity_id, entity_id, entity_id),
                )
                items = [json.loads(row[0]) for row in rows]
        return [
            item
            for item in items
            if (target is None or item["to_entity"] == target)
            and (
                relationship_type is None
                or item["relationship_type"] == relationship_type
            )
        ][:limit]

    def get_entity_network(self, entity_id, depth=2):
        if isinstance(depth, bool) or not isinstance(depth, int) or not 1 <= depth <= 5:
            raise ValueError("depth must be 1 to 5")
        center = self.get_entity(entity_id)
        if center is None:
            raise ValueError("entity does not exist")
        nodes = {entity_id: center}
        edges = {}
        frontier = {entity_id}
        for _ in range(depth):
            following = set()
            for source in frontier:
                for edge in self.get_relationships(source, limit=1000):
                    edges[edge["id"]] = edge
                    for key in ["from_entity", "to_entity"]:
                        node_id = edge[key]
                        if node_id not in nodes:
                            node = self.get_entity(node_id)
                            if node:
                                nodes[node_id] = node
                                following.add(node_id)
            if len(nodes) > 1000 or len(edges) > 5000:
                raise ValueError("network exceeds bounded query size")
            frontier = following
        return {
            "center": center,
            "nodes": list(nodes.values()),
            "edges": list(edges.values()),
            "depth": depth,
        }
