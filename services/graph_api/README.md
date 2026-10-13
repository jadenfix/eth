# Executable ontology graph

Run `python -m services.graph_api.graph_api` for the loopback GraphQL API.
The service imports without cloud credentials. With no `NEO4J_URI`, it uses an
explicit durable SQLite graph at `GRAPH_DB_PATH` (default `data/ontology.sqlite`).
With `NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD`, it executes parameterized
Cypher against the actual Neo4j server. It does not fabricate entity records or
silently switch a failed configured provider to local storage.

`POST /graphql` supports entity creation/update, filtering, relationship creation
and bounded network traversal. Local SQLite writes accept loopback clients;
set `GRAPH_API_TOKEN` to require a Bearer token. Neo4j writes always require that
token. Provider failures are visible as GraphQL errors or HTTP503 health status.
`GET /health` reports the actual selected storage mode.

The existing ontology module delegates these same graph operations, replacing
invalid dynamic-label/property Cypher and eager credential-dependent startup.

`pytest tests/graph_api` exercises actual SQLite+HTTP state, authorization,
invalid inputs, zero-valued filters, relationships and restart persistence.
Set `GRAPH_REQUIRE_NEO4J=1` with an ephemeral Neo4j server to require the real
provider workflow; it is mandatory in the dedicated hosted graph gate. Local
execution without Neo4j explicitly skips that provider test and does not count
as a cloud database proof. Tests use only disposable fictional graph records.

This is a graph storage/query boundary. It does not independently establish real
Ethereum ingestion, entity-resolution accuracy, authorization integration across
all services, or a deployed Neo4j Aura/GCP environment.
