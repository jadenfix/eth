# Visualization Layer

Palantir Foundry-style visualization services for blockchain intelligence.

## Architecture

This layer provides interactive data visualization components that integrate with the semantic fusion layer to deliver rich analytical experiences.

### Components

- **DeckGL Explorer**: WebGL-based network graphs for entity relationships
- **TimeSeries Canvas**: High-performance time-series charts for blockchain metrics  
- **Compliance Map**: Geographic and flow-based compliance visualization
- **Workspace**: Drag & drop dashboard builder

### Integration Points

- **Data Sources**: GraphQL ontology API, REST metrics API, WebSocket streams
- **Backend Services**: Entity resolution, compliance analysis, risk scoring
- **Frontend Framework**: Next.js with TypeScript and Tailwind CSS

## Development

Each visualization component is a self-contained microservice with its own package.json and dependencies.

### Local Development

```bash
# Install dependencies for all visualization services
cd services/visualization
for dir in */; do cd "$dir" && npm install && cd ..; done

# Start development servers
docker-compose up visualization
```

### Production Deployment

Each service has its own Dockerfile and can be deployed independently to GKE.

## Data Flow

1. **Ingestion Layer** → Raw blockchain data
2. **Semantic Fusion Layer** → Entity resolution & ontology 
3. **Visualization Layer** → Interactive dashboards
4. **UX Layer** → User workflows & actions

## Compliance

All visualization components implement:
- Column-level access controls via BigQuery ACLs
- Audit logging for user interactions
- DLP redaction for sensitive data fields
- Real-time compliance monitoring integration
