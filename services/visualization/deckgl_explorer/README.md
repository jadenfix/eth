# Deck.GL Explorer - Blockchain Graph Visualization

Force-directed network graphs for blockchain entity analysis, built with Deck.GL and WebGL for high-performance rendering.

## Purpose

Visualizes blockchain entities and their relationships in an interactive network graph format, similar to Palantir Gotham's graph explorer.

## Features

- Force-directed graph layout for natural clustering
- Interactive node/edge selection and highlighting
- Real-time data updates via WebSocket subscriptions
- Entity type-based color coding
- Risk score-based node sizing
- Tooltip information on hover
- Zoom, pan, and reset controls

## Environment Variables

```bash
# Required for map backgrounds
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1...

# GraphQL endpoint for entity data
GRAPHQL_ENDPOINT=http://localhost:4000/graphql

# WebSocket endpoint for real-time updates
WEBSOCKET_ENDPOINT=ws://localhost:4000/subscriptions
```

## Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Dependencies

- @deck.gl/react: WebGL-based visualization framework
- @deck.gl/graph-layers: Graph-specific layer implementations
- react-map-gl: Map integration for geographical context
- d3-scale: Color scales and data transformations
- d3-scale-chromatic: Predefined color schemes

## Data Format

Expected GraphQL schema for entity relationships:

```graphql
type Node {
  id: ID!
  entity_id: String!
  entity_type: EntityType!
  label: String!
  risk_score: Float
  balance: Float
  metadata: JSON
}

type Edge {
  source: String!
  target: String!
  weight: Float!
  relationship_type: RelationshipType!
  value: Float
  timestamp: String
}

enum EntityType {
  ADDRESS
  CONTRACT
  TOKEN
  TRANSACTION
  BLOCK
}

enum RelationshipType {
  TRANSFER
  APPROVAL
  INTERACTION
  OWNERSHIP
}
```

## Integration

This component integrates with:
- `services/ontology/graph_api.py` - GraphQL entity data
- `services/api_gateway/websocket.py` - Real-time updates
- `services/entity_resolution/pipeline.py` - Entity resolution data
