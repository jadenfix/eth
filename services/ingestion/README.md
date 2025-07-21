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
