# Onchain Command Center

A Palantir-grade blockchain intelligence platform for real-time data fusion, AI-powered analysis, and institutional-grade compliance.

---

## 🚀 Architecture Overview (v3)

```
┌────────────────────────────────────────────────────────────────────────────┐
│  0. Identity & Access                                                      │
│     • Cloud IAM  +  BigQuery Column-Level ACLs  +  Cloud DLP Redaction     │
│     • Audit Logs to Cloud Logging (SOC-2 ready)                            │
├────────────────────────────────────────────────────────────────────────────┤
│  1. Ingestion Layer                                                        │
│     • Cloud Functions  → Pub/Sub  → Dataflow                               │
│       – WS + RPC pulls (Alchemy / Infura) + TheGraph                       │
│       – Normalised to “chain-event” JSON                                   │
│     • Raw & Curated tables land in BigQuery                                │
├────────────────────────────────────────────────────────────────────────────┤
│  2. Semantic Fusion Layer                                                  │
│     • Ontology Service (GraphQL, Neo4j Aura)                               │
│     • Entity-Resolution Pipeline (Vertex AI matching)                      │
├────────────────────────────────────────────────────────────────────────────┤
│  3. Intelligence & Agent Mesh                                              │
│     • Vertex AI Pipelines, GKE Agent Mesh (MEV, liquidations, sanctions)   │
│     • Feedback Loop (Slack buttons) → Pub/Sub → retrain trigger           │
├────────────────────────────────────────────────────────────────────────────┤
│  4. API & VoiceOps Layer                                                   │
│     • gRPC + REST (Cloud Run), WebSocket push, ElevenLabs Gateway          │
├────────────────────────────────────────────────────────────────────────────┤
│  5. Visualization Layer                                                    │
│     • Graph Explorer (deck.gl), Time-Series Canvas, Compliance Map         │
│     • Foundry-style Workspace (drag/drop panels, dashboards)               │
├────────────────────────────────────────────────────────────────────────────┤
│  6. UX & Workflow Builder                                                  │
│     • Next.js + ChakraUI “War-Room”, Dagster, Slack/MS Teams VoiceBot      │
├────────────────────────────────────────────────────────────────────────────┤
│  7. Launch & Growth                                                        │
│     • Token-gated beta, Stripe metering & billing                          │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Prerequisites

- Node.js 18+, Python 3.9+
- Docker (for local services)
- GCP account with BigQuery, Pub/Sub, Vertex AI, Secret Manager, DLP, KMS enabled
- Neo4j AuraDB account (or local Neo4j for dev)
- [Optional] ElevenLabs, Stripe, Slack, Alchemy/Infura API keys

---

## ⚙️ Environment Setup

1. **Clone the repo**
   ```bash
   git clone <repo-url>
   cd onchain-command-center
   ```
2. **Install dependencies**
   ```bash
   npm install
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   ```bash
   cp .env.sample .env
   # Fill in all required keys (see .env.sample for details)
   # Optionally, run scripts/local_dev_env.sh to auto-populate for dev
   ```
4. **(Recommended) Migrate secrets to GCP Secret Manager**
   - Use `tests/e2e/helpers/secret_manager.py` to migrate sensitive keys
   - Update your .env to reference Secret Manager where possible

---

## ☁️ Infrastructure Deployment

1. **Provision GCP resources**
   ```bash
   cd infra/gcp
   terraform init
   terraform plan
   terraform apply
   ```
2. **Provision Neo4j AuraDB**
   - Create an AuraDB instance, update NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env
3. **Enable CMEK (encryption) and CDN (static assets) [optional, prod]**
   - See `tests/e2e/helpers/cmek.py` and `cdn.py`

---

## 🧩 Service Overview

- **Ingestion**: Real-time blockchain data via Alchemy/Infura, Dataflow, Pub/Sub
- **Ontology**: GraphQL API with Neo4j semantic layer (services/ontology/)
- **Entity Resolution**: Vertex AI-powered identity matching (services/entity_resolution/)
- **Agent Mesh**: MEV, whale tracking, sanctions monitoring (services/agents/)
- **Risk AI**: Anomaly detection, fraud analysis (services/risk_ai/)
- **ZK-Attestation**: Zero-knowledge proof generation/verification (zk_attestation/)
- **Gemini Explainability**: AI-powered signal explanations (ai_services/gemini_explain/)
- **Action Executor**: Autonomous action dispatcher (action_executor/)
- **VoiceOps**: ElevenLabs TTS/STT integration (services/voiceops/)
- **Visualization**: Graph Explorer, Time-Series Canvas, Compliance Map (services/visualization/)
- **Dashboard**: Next.js real-time war room (services/ui/nextjs-app/)
- **Workflow Builder**: Dagster/Vertex pipelines (services/workflow_builder/)

---

## 🧪 Running End-to-End Tests

1. **Core & Integration Tests**
   ```bash
   python test_runner_integration.py --mode all --verbose
   # Or run by tier:
   pytest tests/e2e/tier0/ -v
   pytest tests/e2e/tier1/ -v
   pytest tests/e2e/tier2/ -v
   pytest tests/e2e/tier3/ -v
   ```
2. **V3 Feature Tests**
   ```bash
   pytest tests/e2e/graph_sync/
   pytest tests/e2e/zk_attestation/
   pytest tests/e2e/gemini_explain/
   pytest tests/e2e/action_executor/
   pytest tests/e2e/voice_alerts/
   pytest tests/e2e/visualization/
   ```
3. **CI/CD**
   - See TESTING_SERVICES.md for CI integration and troubleshooting

---

## 🖥️ Using the Platform

- **CLI**: Use scripts and test runners for ingestion, pipeline, and agent tasks
- **API**: REST/GraphQL endpoints (see services/api_gateway/proto/onchain_api.proto)
- **UI**: Start the Next.js dashboard
   ```bash
   cd services/ui/nextjs-app
   npm run dev
   # Visit http://localhost:3000
   ```
- **Visualization**: Access explorer, canvas, compliance map via UI tabs
- **Workflow**: Build/trigger signals in Dagster UI or via API
- **VoiceOps**: Use dashboard voice features or Slack integration

---

## ✅ Greenlight Checklist (Demo/Production)

- [ ] Ingest path live; curated BigQuery rows updating
- [ ] Ontology GraphQL returns >0 entities; tag search works
- [ ] ER pipeline collapsed test cluster (see test log)
- [ ] Agent emitted signal; visible in dashboard & Slack
- [ ] Column masking verified for Analyst role
- [ ] Audit log shows last 10 user queries w/ principals
- [ ] Feedback button produced retrain job event
- [ ] Token gate enforced (wallet w/out token denied)
- [ ] Stripe test invoice generated from API usage

---

## 📚 Documentation & Frontend Development

- See `docs/` for:
  - system_architecture_v3.md (architecture)
  - mission.md (vision)
  - go_to_market_pitch.md, vc_alignment.md (strategy)
  - system_architecture_v3.png (diagram)
- See `TESTING_SERVICES.md` for test, CI, and troubleshooting details
- See `services/ui/nextjs-app/FRONTEND_README.md` for frontend component and API usage
- See `prompts/` for E2E test blueprints and Playwright specs

---

## 🆘 Troubleshooting & Support

- **Common Issues**: See TESTING_SERVICES.md and IMPLEMENTATION_PROGRESS_SUMMARY.md
- **Environment**: Use `tests/e2e/helpers/env_utils.py` to validate .env and integration readiness
- **Secrets**: Use Secret Manager for production keys
- **Performance**: Run Tier 3 tests and monitor logs
- **Contact**: Open an issue or contact maintainers for help

---

## 🤝 Contributing

PRs welcome! Please see CONTRIBUTING.md (if available) and open issues for discussion.

## License

MIT