# Ingestion Service

Real-time blockchain data ingestion service that pulls data from Ethereum via Alchemy/Infura APIs and publishes normalized events to Pub/Sub.

## Features

- Real-time block and transaction monitoring
- Canonical event normalization
- High-throughput Pub/Sub publishing
- Structured logging with trace IDs
- Error handling and retry logic
- Prometheus metrics exposure

## Environment Variables

```bash
ALCHEMY_API_KEY=your-alchemy-key
GOOGLE_CLOUD_PROJECT=your-gcp-project
LOG_LEVEL=info
PUBSUB_TOPIC=raw-chain-events
```

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ALCHEMY_API_KEY=your-key
export GOOGLE_CLOUD_PROJECT=your-project

# Run ingester
python ethereum_ingester.py
```

## Docker

```bash
docker build -t ingestion-service .
docker run -e ALCHEMY_API_KEY=your-key ingestion-service
```

## Schema

The service publishes events in this canonical format:

```json
{
  "block_number": 18500000,
  "transaction_hash": "0x...",
  "log_index": 0,
  "contract_address": "0x...",
  "event_name": "TRANSFER",
  "event_data": {
    "from": "0x...",
    "to": "0x...",
    "value": "1000000000000000000"
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "chain_id": 1,
  "ingestion_timestamp": "2024-01-01T00:00:01Z"
}
```

## Monitoring

- Prometheus metrics on `:9090/metrics`
- Structured JSON logs to stdout
- Health check on `:8080/health`

## Executable read-only event engine

`EventNormalizer` converts actual Ethereum quantities (hex or integers) and receipts
to the canonical chain event, including flat fields consumed by downstream agents.
USD values stay `null` unless a price provider is explicitly supplied.
`MessagePublisher` waits for the provider publication future; failed sends propagate
so blocks are not falsely advanced. `MessageProcessor` commits deliveries to SQLite
before acknowledgement and deduplicates successful replay across restarts.

```bash
PYTHONPATH=. python scripts/check_event_replay.py
pytest tests/behavioral -q
```

The replay command launches a real loopback JSON-RPC server with explicitly labeled
block/receipt fixtures, calls it through the real Web3 HTTP client, runs the actual
normalizer and MEV engine, and verifies durable SQLite replay/restart behavior.
It performs no live chain, funded, cloud or paid-provider calls. Gas and sandwich
signals are heuristics with `verified_attack: false`, not verified MEV attacks.
Sandwich detection requires an ordered attacker/victim/attacker sequence, distinct
transaction hashes and the same target contract. Missing USD valuations never
produce whale alerts.

Entity resolution requires explicit observations or an authenticated BigQuery
client. Missing observations/providers fail; behavioral grouping is an unverified
candidate, with separately labeled supplied-model confidence. `GraphUpdater` stores
canonical JSON payloads compatible with the ontology API. Vertex job submission
requires an explicit pipeline template and returns SUBMITTED, never a fabricated
completed result. Live adapters and model accuracy require their own integration
receipts.
