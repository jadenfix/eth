# Onchain Command Center

A Palantir-grade blockchain intelligence platform for real-time data fusion, AI-powered analysis, and institutional-grade compliance.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Identity & Access → Ingestion → Semantic Fusion → Intelligence     │
│  Cloud IAM + DLP  → Dataflow   → Ontology + ER   → Agent Mesh       │
│                    → BigQuery  → Neo4j Graph    → Vertex AI         │
└─────────────────────────────────────────────────────────────────────┘
```

## Runnable local graph workspace

The local gateway and JavaScript SDK now support a real durable graph workflow.
Node 22.13+ is required (CI uses Node 24). No npm install or cloud credentials are
needed for the gateway or SDK themselves.

```bash
npm run build:api
npm run build:sdk
npm run test:api
npm run dev:graph
```

Open http://127.0.0.1:8080. Add entities, connect them, inspect their multi-hop
network, and search records. The browser reads actual API counts, and records
persist in `services/api_gateway/data/graph.sqlite` across restarts. Optional
`GRAPH_DB_PATH`, `PORT`, and `HOST` configure the server. Keep the default loopback
binding for local use. Set `API_TOKEN` to require a Bearer token for API clients;
the browser workspace currently supports the loopback, token-free local mode.

```js
import {OnchainClient} from './sdk/js/index.js';
const client = new OnchainClient('http://127.0.0.1:8080');
const wallet = await client.createEntity({
  type: 'ADDRESS', name: 'Treasury', address: '0x' + 'a'.repeat(40)
});
console.log(await client.getNetwork(wallet.id));
```

HTTP API: `POST /v1/entities`, `GET /v1/entities/search`,
`GET /v1/entities/:id`, `POST /v1/relationships`,
`GET /v1/entities/:id/network?depth=2`, and `GET /v1/health`.
Entity addresses are validated and unique, relationships require existing
endpoints, and missing records return 404. `/v1/events` and `/v1/signals` are
honestly empty until a source is connected; `/v1/feedback` rejects unknown signals.
Risk scores remain null. This path performs no chain transactions or paid AI calls.

The `Durable local graph workflow` CI runs the actual HTTP SDK workflow, failure
cases, restart persistence, and real Chromium form/network/search checks at desktop
and mobile widths. To run the browser check locally, install the gateway's dev
dependencies and Chromium, then run `npm --prefix services/api_gateway run test:browser`.

The legacy Next.js monitoring pages and GCP/Neo4j/AI services below are separate
cloud scaffolds, including sample dashboard data. The local graph workspace does
not validate their live ingestion, cloud deployment, compliance, or AI claims.

## Cloud scaffold setup


1. **Prerequisites**
   ```bash
   # Install dependencies
   npm install
   pip install -r requirements.txt
   
   # Setup GCP credentials
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Environment Setup**
   ```bash
   cp .env.sample .env
   # Edit .env with your credentials
   ```

3. **Infrastructure Deployment**
   ```bash
   cd infra/gcp
   terraform init
   terraform plan
   terraform apply
   ```

4. **Local Development**
   ```bash
   ./scripts/local_dev_env.sh
   ```

## Services

- **Ingestion**: Real-time blockchain data via Alchemy/Infura
- **Ontology**: GraphQL API with Neo4j semantic layer  
- **Entity Resolution**: Vertex AI-powered identity matching
- **Agent Mesh**: MEV, whale tracking, sanctions monitoring
- **Risk AI**: Anomaly detection, fraud analysis
- **VoiceOps**: ElevenLabs TTS/STT integration
- **Dashboard**: Next.js real-time war room

## Development

See individual service READMEs for detailed setup instructions.

## License

MIT