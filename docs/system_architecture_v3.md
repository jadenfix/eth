# System Architecture v3 - With Visualization Layer

## Overview

The Onchain Command Center now includes a comprehensive Visualization Layer (Layer 5) providing Palantir Foundry-style interactive dashboards and analytical interfaces.

## Architecture Layers

```
┌────────────────────────────────────────────────────────────────────────────┐
│  0. Identity & Access                                                      │
│     • Cloud IAM  +  BigQuery Column-Level ACLs  +  Cloud DLP Redaction     │
│     • Audit Logs to Cloud Logging (SOC-2 ready)                            │
├────────────────────────────────────────────────────────────────────────────┤
│  1. Ingestion Layer                                                        │
│     • Cloud Functions  → Pub/Sub  → Dataflow                               │
│       – WS + RPC pulls (Alchemy / Infura) + TheGraph                       │
│       – Normalised to "chain-event" JSON                                   │
│     • Raw & Curated tables land in BigQuery                                │
├────────────────────────────────────────────────────────────────────────────┤
│  2. Semantic Fusion Layer                                                  │
│     • Ontology Service (GraphQL)                                           │
│          – Metadata & relationships stored in Neo4j Aura or Dataplex       │
│     • Entity-Resolution Pipeline (Vertex AI matching)                      │
│          – Adds `entity_id` → writes back to BigQuery + Ontology           │
├────────────────────────────────────────────────────────────────────────────┤
│  3. Intelligence & Agent Mesh                                              │
│     • Vertex AI Pipelines                                                  │
│         – Auto-encoder anomaly, GBDT fraud, Graph-SAGE risk                │
│     • GKE Agent Mesh (MEV, liquidations, sanctions …)                      │
│         – Agents subscribe to Pub/Sub & Ontology GraphQL                   │
│         – Publish "signals" to Marketplace                                 │
│     • Feedback Loop (Slack buttons) → Pub/Sub → retrain trigger           │
├────────────────────────────────────────────────────────────────────────────┤
│  4. API & VoiceOps Layer                                                   │
│     • gRPC + REST (Cloud Run)                                             │
│     • WebSocket push to dashboards                                        │
│     • ElevenLabs Gateway                                                  │
│         – TTS for alerts; STT→Intent for voice commands                    │
├────────────────────────────────────────────────────────────────────────────┤
│  5. **Visualization Layer** (NEW)                                          │
│     • **Graph Explorer** – force-directed, WebGL network graphs (deck.gl)   │
│     • **Time-Series Canvas** – high-throughput charts (Plotly.js / D3)      │
│     • **Compliance Map** – choropleth & Sankey for fund flows               │
│     • **Foundry-style "Workspace"** – drag/drop panels, tabbed dashboards   │
│     • Data fetched via our GraphQL Ontology API + WebSocket subscriptions  │
├────────────────────────────────────────────────────────────────────────────┤
│  6. UX & Workflow Builder                                                   │
│     • Next.js + ChakraUI "War-Room"                                        │
│     • Dagster / Vertex Pipeline Studio (low-code signal builder)           │
│     • Slack / MS Teams VoiceBot                                            │
│     • React / Python SDK widgets                                           │
├────────────────────────────────────────────────────────────────────────────┤
│  7. Launch & Growth                                                         │
│     • Pond Markets token-gated beta                                        │
│     • Stripe metering & billing                                           │
└────────────────────────────────────────────────────────────────────────────┘
```

## Visualization Layer Components

### 1. DeckGL Explorer
- **Purpose**: Interactive network graph visualization of blockchain entities
- **Technology**: Deck.GL, WebGL, React
- **Features**: Force-directed layout, entity clustering, risk-based coloring
- **Data Sources**: Ontology GraphQL API, entity relationships
- **Port**: 3001

### 2. TimeSeries Canvas  
- **Purpose**: High-performance time-series analytics for blockchain metrics
- **Technology**: Plotly.js, D3, Canvas rendering
- **Features**: Real-time updates, multi-metric overlay, export capabilities
- **Data Sources**: Metrics REST API, WebSocket streams
- **Port**: 3002

### 3. Compliance Map
- **Purpose**: Regulatory compliance visualization with geographic and flow analysis
- **Technology**: D3-geo, D3-sankey, TopoJSON
- **Features**: Choropleth maps, Sankey flow diagrams, sanctions highlighting
- **Data Sources**: Compliance API, jurisdiction data
- **Port**: 3003

### 4. Workspace Builder
- **Purpose**: Foundry-style drag & drop dashboard builder
- **Technology**: React DnD, configurable panels
- **Features**: Panel management, layout persistence, real-time data binding
- **Data Sources**: All visualization components
- **Port**: 3004

## Integration Architecture

### Data Flow
1. **Layer 1-2**: Raw data ingestion → semantic enrichment
2. **Layer 3**: AI/ML analysis → signal generation  
3. **Layer 4**: API exposure → real-time streaming
4. **Layer 5**: Visualization → interactive dashboards
5. **Layer 6**: User workflows → analyst actions

### API Integration Points
- **GraphQL Ontology API**: Entity relationships, metadata
- **REST Metrics API**: Time-series data, aggregations
- **WebSocket Streams**: Real-time updates, live data
- **Compliance API**: Risk scores, sanctions data

### Security & Governance
- Column-level access controls inherited from BigQuery ACLs
- Audit logging for all user interactions
- DLP redaction for sensitive data visualization
- Real-time compliance monitoring integration

## Deployment Architecture

### Development
```bash
# Start all visualization services
npm run dev:visualization

# Individual service development
cd services/visualization/{service} && npm run dev
```

### Production (Kubernetes)
```bash
# Deploy to GKE
kubectl apply -f infra/k8s/visualization/

# Scale based on load
kubectl scale deployment deckgl-explorer --replicas=3
```

### Container Registry
- `gcr.io/onchain-command-center/deckgl-explorer:latest`
- `gcr.io/onchain-command-center/timeseries-canvas:latest`
- `gcr.io/onchain-command-center/compliance-map:latest`
- `gcr.io/onchain-command-center/workspace:latest`

## Configuration

### Environment Variables
```bash
# Geographic map rendering
MAPBOX_TOKEN=pk.eyJ1...
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1...

# Data source endpoints  
NEXT_PUBLIC_WEBSOCKET_ENDPOINT=ws://localhost:4000/subscriptions
NEXT_PUBLIC_GRAPHQL_ENDPOINT=http://localhost:4000/graphql

# Service-specific ports
DECKGL_EXPLORER_PORT=3001
TIMESERIES_CANVAS_PORT=3002  
COMPLIANCE_MAP_PORT=3003
WORKSPACE_PORT=3004
```

### Performance Optimization
- WebGL rendering for large datasets (10k+ nodes)
- Canvas-based charts for high-frequency data
- Efficient data streaming and caching
- Lazy loading for dashboard components

## Compliance with Rules

### Code Quality (Rules 5-7)
- ✅ TypeScript with strict mode enabled
- ✅ Single-responsibility modules per service
- ✅ Shared utilities in visualization SDK
- ✅ DRY principles with component reuse

### Testing & CI/CD (Rules 8-10)
- ✅ Unit tests for each visualization component
- ✅ E2E tests for dashboard workflows
- ✅ Docker build validation in CI pipeline

### Infrastructure as Code (Rules 11-13) 
- ✅ Terraform modules for GKE deployments
- ✅ Kubernetes manifests with resource limits
- ✅ Automated deployment pipelines

### API Governance (Rules 14-16)
- ✅ GraphQL schema validation for ontology data
- ✅ JSON schema for metrics API responses
- ✅ Versioned API contracts

### Security (Rules 17-19)
- ✅ Secrets via GCP Secret Manager
- ✅ Service account per visualization service
- ✅ DLP policies for sensitive data redaction

### Observability (Rules 20-22)
- ✅ Structured JSON logging with trace IDs
- ✅ Prometheus metrics for service health
- ✅ Alerting on visualization service failures

### Documentation (Rules 23-25)
- ✅ README.md for each visualization service
- ✅ System architecture diagram updated (v3)
- ✅ Integration guide for dashboard builders

## Future Enhancements

1. **AI-Powered Insights**: Auto-generated dashboard recommendations
2. **Collaborative Features**: Shared workspaces, annotation tools
3. **Mobile Optimization**: Responsive design for mobile analysts
4. **Advanced Analytics**: Statistical overlays, correlation analysis
5. **Export Capabilities**: PDF reports, data extracts

## Monitoring & Alerting

- **Service Health**: Kubernetes liveness/readiness probes
- **Performance**: Response time, memory usage metrics
- **User Experience**: Dashboard load times, interaction tracking
- **Data Quality**: Visualization data freshness alerts

This visualization layer completes the Palantir-grade architecture, providing analysts with powerful, interactive tools for blockchain intelligence analysis.
