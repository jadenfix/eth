# Onchain Command Center - Technical Documentation

## Table of Contents
1. [Backend Architecture](#backend-architecture)
2. [API Reference](#api-reference)
3. [Frontend Architecture](#frontend-architecture)
4. [Component Library](#component-library)
5. [Integration Patterns](#integration-patterns)
6. [Development Workflow](#development-workflow)
7. [Performance Optimization](#performance-optimization)
8. [Testing Strategy](#testing-strategy)

---

## Backend Architecture

### Core Services Overview

The backend follows a microservices architecture with 6 main layers:

#### Layer 0: Identity & Access Management
- **Location**: `services/access_control/`
- **Key Components**:
  - `audit_sink.py`: Comprehensive audit logging
  - `policies.yaml`: Access control policies
  - BigQuery column-level ACLs
  - Cloud DLP data masking

#### Layer 1: Ingestion Layer
- **Location**: `services/ethereum_ingester/`
- **Key Components**:
  - `ethereum_ingester.py`: Real-time blockchain data ingestion
  - `ethereum_ingester_realtime.py`: WebSocket-based ingestion
  - Pub/Sub message processing
  - Dataflow pipeline integration

#### Layer 2: Semantic Fusion Layer
- **Location**: `services/ontology/`, `services/entity_resolution/`
- **Key Components**:
  - `graph_api.py`: GraphQL API for ontology queries
  - `pipeline.py`: ML-based entity resolution
  - Neo4j graph database integration
  - Vertex AI pipeline orchestration

#### Layer 3: Intelligence & Agent Mesh
- **Location**: `services/agents/`, `services/mev_agent/`
- **Key Components**:
  - `mev_agent.py`: MEV detection algorithms
  - `mev_watch/agent.py`: Real-time MEV monitoring
  - Signal generation and publishing
  - Risk scoring models

#### Layer 4: API & VoiceOps Layer
- **Location**: `services/api_gateway/`, `services/voiceops/`
- **Key Components**:
  - `onchain_api.proto`: gRPC API definitions
  - `voice_service.py`: ElevenLabs TTS/STT integration
  - WebSocket real-time updates
  - REST API endpoints

#### Layer 5: Visualization Layer (v3)
- **Location**: `services/visualization/`
- **Key Components**:
  - `deckgl_explorer/`: Network graph visualization
  - `timeseries_canvas/`: Time-series charts
  - `compliance_map/`: Geographic compliance mapping
  - `workspace/`: Foundry-style workspace management

### Data Flow Architecture

```
Blockchain Data → Ingestion → BigQuery → Entity Resolution → Neo4j
                                 ↓
                            Pub/Sub Topics
                                 ↓
                            Agent Mesh → Signals → Dashboard
                                 ↓
                            VoiceOps → Alerts
```

### Key Backend Technologies

- **Python 3.9+**: Core backend services
- **FastAPI**: REST API framework
- **gRPC**: High-performance API communication
- **Google Cloud Platform**: BigQuery, Pub/Sub, Vertex AI, DLP
- **Neo4j AuraDB**: Graph database for ontology
- **ElevenLabs**: Voice operations (TTS/STT)
- **Dagster**: Workflow orchestration

---

## API Reference

### GraphQL API (Ontology)

**Endpoint**: `/graphql`

#### Core Queries

```graphql
# Get entities with pagination
query GetEntities($limit: Int, $offset: Int) {
  entities(limit: $limit, offset: $offset) {
    id
    type
    addresses {
      address
      label
    }
    confidence
    labels
  }
}

# Get entity by ID
query GetEntity($id: ID!) {
  entity(id: $id) {
    id
    type
    addresses {
      address
      label
    }
    transactions {
      hash
      value
      timestamp
    }
    relationships {
      type
      target {
        id
        type
      }
    }
  }
}

# Search entities
query SearchEntities($query: String!, $type: EntityType) {
  searchEntities(query: $query, type: $type) {
    id
    type
    addresses {
      address
      label
    }
    confidence
  }
}
```

#### Mutations

```graphql
# Create entity
mutation CreateEntity($input: CreateEntityInput!) {
  createEntity(input: $input) {
    id
    type
    addresses {
      address
      label
    }
  }
}

# Update entity labels
mutation UpdateEntityLabels($id: ID!, $labels: [String!]!) {
  updateEntityLabels(id: $id, labels: $labels) {
    id
    labels
  }
}
```

### REST API Endpoints

#### System Status
```http
GET /health
GET /system/status
GET /system/metrics
```

#### Entity Management
```http
GET /api/entities
GET /api/entities/{id}
POST /api/entities
PUT /api/entities/{id}
DELETE /api/entities/{id}
```

#### Signal Management
```http
GET /api/signals
GET /api/signals/{id}
POST /api/signals
PUT /api/signals/{id}/status
```

#### Voice Operations
```http
POST /api/voice/tts
POST /api/voice/stt
WS /api/voice/stream
```

### WebSocket API

#### Real-time Updates
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to entity updates
ws.send(JSON.stringify({
  type: 'subscribe',
  channel: 'entity_updates',
  entity_id: 'ENT_001'
}));

// Listen for updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Entity update:', data);
};
```

---

## Frontend Architecture

### Technology Stack

- **Next.js 14**: React framework with SSR/SSG
- **TypeScript**: Type-safe development
- **Chakra UI**: Component library with custom theme
- **Framer Motion**: Animations and transitions
- **React DnD**: Drag and drop functionality
- **Canvas API**: High-performance visualizations
- **GraphQL**: Data fetching with Apollo Client

### Project Structure

```
services/ui/nextjs-app/
├── src/
│   ├── components/
│   │   ├── atoms/          # Basic UI elements
│   │   ├── molecules/      # Compound components
│   │   ├── organisms/      # Complex UI sections
│   │   └── layout/         # Layout components
│   ├── pages/              # Next.js pages
│   ├── theme/              # Design system
│   ├── providers/          # Context providers
│   └── lib/                # Utilities and helpers
├── public/                 # Static assets
└── styles/                 # Global styles
```

### Atomic Design System

#### Atoms (Basic Components)

```tsx
// Button Component
<Button 
  variant="primary" 
  size="md" 
  leftIcon={<Icon name="search" />}
  onClick={handleClick}
>
  Search Addresses
</Button>

// Icon Component
<Icon 
  name="ethereum" 
  size="lg" 
  color="blue.500" 
/>

// Spinner Component
<Spinner 
  variant="dots" 
  size="lg" 
  overlay={true}
/>
```

#### Molecules (Compound Components)

```tsx
// Navigation Bar
<NavBar 
  user={user}
  notifications={notifications}
  onSearch={handleSearch}
  onNotificationClick={handleNotification}
/>

// Sidebar Navigation
<SideBar 
  items={navigationItems}
  isCollapsed={isCollapsed}
  onItemClick={handleNavigation}
  onToggle={handleToggle}
/>

// Panel Header
<PanelHeader 
  title="Network Graph"
  onMinimize={handleMinimize}
  onMaximize={handleMaximize}
  onClose={handleClose}
  draggable={true}
/>
```

#### Organisms (Complex Components)

```tsx
// Dockable Layout
<DockableLayout 
  panels={panels}
  onPanelUpdate={handlePanelUpdate}
  onPanelClose={handlePanelClose}
  snapToGrid={true}
  gridSize={20}
/>

// Graph Explorer
<GraphExplorer 
  data={graphData}
  onNodeClick={handleNodeClick}
  onEdgeClick={handleEdgeClick}
  layout="force"
  showControls={true}
/>
```

### Theme System

#### Color Palette

```typescript
// theme/colors.ts
export const colors = {
  primary: {
    50: '#E6F3FF',
    500: '#3182CE',
    900: '#1A365D'
  },
  risk: {
    low: '#10B981',
    medium: '#F59E0B',
    high: '#EF4444',
    critical: '#DC2626'
  },
  entity: {
    address: '#3B82F6',
    contract: '#8B5CF6',
    token: '#10B981',
    transaction: '#F59E0B',
    block: '#6B7280'
  }
};
```

#### Typography

```typescript
// theme/typography.ts
export const typography = {
  fonts: {
    heading: 'Inter, sans-serif',
    body: 'Inter, sans-serif',
    mono: 'JetBrains Mono, monospace'
  },
  fontSizes: {
    xs: '0.75rem',
    sm: '0.875rem',
    md: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem'
  }
};
```

---

## Component Library

### Core Components

#### 1. Dashboard Component
```tsx
// src/components/Dashboard.tsx
interface DashboardProps {
  layout: 'grid' | 'flexible' | 'workspace';
  panels: Panel[];
  onPanelUpdate: (panel: Panel) => void;
  theme?: 'light' | 'dark';
}

<Dashboard 
  layout="workspace"
  panels={dashboardPanels}
  onPanelUpdate={handlePanelUpdate}
  theme="dark"
/>
```

#### 2. Graph Explorer
```tsx
// src/components/organisms/GraphExplorer.tsx
interface GraphExplorerProps {
  data: GraphData;
  layout: 'force' | 'hierarchical' | 'circular';
  onNodeClick: (node: Node) => void;
  onEdgeClick: (edge: Edge) => void;
  showControls: boolean;
  enableZoom: boolean;
  enablePan: boolean;
}

<GraphExplorer 
  data={networkData}
  layout="force"
  onNodeClick={handleNodeClick}
  onEdgeClick={handleEdgeClick}
  showControls={true}
  enableZoom={true}
  enablePan={true}
/>
```

#### 3. Workspace Layout
```tsx
// src/components/organisms/DockableLayout.tsx
interface DockableLayoutProps {
  panels: Panel[];
  onPanelUpdate: (panel: Panel) => void;
  onPanelClose: (panelId: string) => void;
  snapToGrid: boolean;
  gridSize: number;
  allowOverlap: boolean;
}

<DockableLayout 
  panels={workspacePanels}
  onPanelUpdate={handlePanelUpdate}
  onPanelClose={handlePanelClose}
  snapToGrid={true}
  gridSize={20}
  allowOverlap={false}
/>
```

### Page Components

#### 1. Main Dashboard (index.tsx)
```tsx
// pages/index.tsx
export default function Dashboard() {
  return (
    <Layout>
      <Dashboard 
        layout="workspace"
        panels={[
          {
            id: 'network-graph',
            type: 'graph-explorer',
            title: 'Network Graph',
            position: { x: 0, y: 0, width: 600, height: 400 }
          },
          {
            id: 'transactions',
            type: 'data-table',
            title: 'Recent Transactions',
            position: { x: 600, y: 0, width: 400, height: 300 }
          }
        ]}
      />
    </Layout>
  );
}
```

#### 2. Explorer Page
```tsx
// pages/explorer.tsx
export default function Explorer() {
  return (
    <Layout>
      <GraphExplorer 
        data={explorerData}
        layout="force"
        onNodeClick={handleNodeClick}
        showControls={true}
      />
    </Layout>
  );
}
```

#### 3. Analytics Page
```tsx
// pages/analytics.tsx
export default function Analytics() {
  return (
    <Layout>
      <DockableLayout 
        panels={analyticsPanels}
        onPanelUpdate={handlePanelUpdate}
        snapToGrid={true}
      />
    </Layout>
  );
}
```

---

## Integration Patterns

### Backend-Frontend Integration

#### 1. GraphQL Integration
```tsx
// lib/graphql/client.ts
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';

const httpLink = createHttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql',
});

export const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
});

// hooks/useEntities.ts
import { useQuery, gql } from '@apollo/client';

const GET_ENTITIES = gql`
  query GetEntities($limit: Int) {
    entities(limit: $limit) {
      id
      type
      addresses {
        address
        label
      }
    }
  }
`;

export function useEntities(limit: number = 10) {
  return useQuery(GET_ENTITIES, {
    variables: { limit },
    pollInterval: 5000, // Refresh every 5 seconds
  });
}
```

#### 2. WebSocket Integration
```tsx
// hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url: string, onMessage: (data: any) => void) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      setIsConnected(true);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.current.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.current?.close();
    };
  }, [url, onMessage]);

  const sendMessage = (message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, sendMessage };
}
```

#### 3. REST API Integration
```tsx
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = {
  async get(endpoint: string) {
    const response = await fetch(`${API_BASE}${endpoint}`);
    return response.json();
  },

  async post(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async put(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  async delete(endpoint: string) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
    });
    return response.json();
  },
};

// hooks/useApi.ts
export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = async (method: keyof typeof api, endpoint: string, data?: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await api[method](endpoint, data);
      return result;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, request };
}
```

### Visualization Integration

#### 1. Deck.GL Integration
```tsx
// components/visualizations/DeckGLMap.tsx
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer } from '@deck.gl/layers';

interface DeckGLMapProps {
  data: any[];
  viewState: any;
  onViewStateChange: (viewState: any) => void;
}

export function DeckGLMap({ data, viewState, onViewStateChange }: DeckGLMapProps) {
  const layers = [
    new ScatterplotLayer({
      id: 'scatter-plot',
      data,
      pickable: true,
      opacity: 0.8,
      stroked: true,
      filled: true,
      radiusScale: 6,
      radiusMinPixels: 1,
      radiusMaxPixels: 100,
      lineWidthMinPixels: 1,
      getPosition: (d: any) => [d.longitude, d.latitude],
      getRadius: (d: any) => Math.sqrt(d.exits),
      getFillColor: (d: any) => [255, 140, 0],
      getLineColor: (d: any) => [0, 0, 0],
    }),
  ];

  return (
    <DeckGL
      initialViewState={viewState}
      controller={true}
      layers={layers}
      onViewStateChange={onViewStateChange}
    />
  );
}
```

#### 2. D3.js Integration
```tsx
// components/visualizations/D3Network.tsx
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface D3NetworkProps {
  data: {
    nodes: any[];
    links: any[];
  };
  width: number;
  height: number;
}

export function D3Network({ data, width, height }: D3NetworkProps) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const simulation = d3.forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.links).id((d: any) => d.id))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
      .selectAll('line')
      .data(data.links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.value));

    const node = svg.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', 5)
      .attr('fill', '#69b3a2')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);
    });

    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return () => simulation.stop();
  }, [data, width, height]);

  return (
    <svg ref={svgRef} width={width} height={height}>
      <g />
    </svg>
  );
}
```

---

## Development Workflow

### Environment Setup

#### 1. Backend Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.sample .env
# Edit .env with your credentials

# Run backend services
python start_services.py

# Run tests
python test_runner_integration.py --mode all --verbose
```

#### 2. Frontend Development
```bash
# Navigate to frontend directory
cd services/ui/nextjs-app

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

### Development Commands

#### Backend
```bash
# Start all services
python start_services.py

# Run specific service
python -m services.ethereum_ingester.ethereum_ingester

# Run tests by tier
pytest tests/e2e/tier0/ -v
pytest tests/e2e/tier1/ -v
pytest tests/e2e/tier2/ -v
pytest tests/e2e/tier3/ -v

# Run integration tests
python test_runner_integration.py --mode integration
```

#### Frontend
```bash
# Development server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Testing
npm run test
npm run test:watch
npm run test:coverage

# Build
npm run build
npm run start
```

### Code Quality

#### Backend Standards
- **Type Hints**: All functions must have type annotations
- **Docstrings**: Comprehensive docstrings for all modules and functions
- **Error Handling**: Proper exception handling with logging
- **Testing**: Minimum 80% test coverage
- **Linting**: Black, isort, flake8 compliance

#### Frontend Standards
- **TypeScript**: Strict type checking enabled
- **Component Structure**: Atomic design principles
- **Accessibility**: ARIA labels and keyboard navigation
- **Performance**: Memoization and lazy loading
- **Testing**: Jest and React Testing Library

---

## Performance Optimization

### Backend Optimization

#### 1. Database Optimization
```python
# BigQuery optimization
def optimize_bigquery_queries():
    # Use clustering for frequently queried columns
    clustering_fields = ['block_number', 'timestamp', 'from_address']
    
    # Partition by date for time-series data
    partition_field = 'DATE(timestamp)'
    
    # Use materialized views for complex aggregations
    materialized_view_query = """
    CREATE MATERIALIZED VIEW `project.dataset.mv_daily_stats`
    AS SELECT 
        DATE(timestamp) as date,
        COUNT(*) as transaction_count,
        SUM(value) as total_value
    FROM `project.dataset.transactions`
    GROUP BY DATE(timestamp)
    """
```

#### 2. Caching Strategy
```python
# Redis caching for frequently accessed data
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiry=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiry=600)
def get_entity_by_id(entity_id: str):
    # Expensive database query
    pass
```

#### 3. Async Processing
```python
# Async processing for I/O operations
import asyncio
import aiohttp

async def fetch_multiple_addresses(addresses: List[str]):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for address in addresses:
            task = fetch_address_data(session, address)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def fetch_address_data(session: aiohttp.ClientSession, address: str):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}"
    async with session.get(url) as response:
        return await response.json()
```

### Frontend Optimization

#### 1. Component Optimization
```tsx
// Memoized components for expensive operations
import React, { useMemo, useCallback } from 'react';

const ExpensiveComponent = React.memo(({ data, onUpdate }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      processed: expensiveCalculation(item)
    }));
  }, [data]);

  const handleUpdate = useCallback((id, value) => {
    onUpdate(id, value);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <DataItem 
          key={item.id} 
          data={item} 
          onUpdate={handleUpdate}
        />
      ))}
    </div>
  );
});
```

#### 2. Code Splitting
```tsx
// Dynamic imports for code splitting
import dynamic from 'next/dynamic';

const GraphExplorer = dynamic(() => import('../components/GraphExplorer'), {
  loading: () => <Spinner />,
  ssr: false
});

const AnalyticsDashboard = dynamic(() => import('../components/AnalyticsDashboard'), {
  loading: () => <Spinner />,
  ssr: false
});
```

#### 3. Virtualization for Large Lists
```tsx
// Virtualized list for performance
import { FixedSizeList as List } from 'react-window';

const VirtualizedList = ({ items }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </List>
  );
};
```

---

## Testing Strategy

### Backend Testing

#### 1. Unit Tests
```python
# tests/unit/test_ethereum_ingester.py
import pytest
from unittest.mock import Mock, patch
from services.ethereum_ingester.ethereum_ingester import EthereumIngester

class TestEthereumIngester:
    @pytest.fixture
    def ingester(self):
        return EthereumIngester()
    
    @pytest.fixture
    def mock_block_data(self):
        return {
            'number': 18500000,
            'timestamp': 1234567890,
            'transactions': [
                {
                    'hash': '0x123...',
                    'from': '0xabc...',
                    'to': '0xdef...',
                    'value': '1000000000000000000'
                }
            ]
        }
    
    def test_process_block(self, ingester, mock_block_data):
        with patch('services.ethereum_ingester.ethereum_ingester.Web3') as mock_web3:
            mock_web3_instance = Mock()
            mock_web3_instance.eth.get_block.return_value = mock_block_data
            mock_web3.return_value = mock_web3_instance
            
            result = ingester.process_block(18500000)
            assert result is not None
            assert len(result['transactions']) == 1
```

#### 2. Integration Tests
```python
# tests/integration/test_pipeline_integration.py
import pytest
from services.ethereum_ingester.ethereum_ingester import EthereumIngester
from services.entity_resolution.pipeline import EntityResolutionPipeline

class TestPipelineIntegration:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        # Test complete pipeline from ingestion to entity resolution
        ingester = EthereumIngester()
        er_pipeline = EntityResolutionPipeline()
        
        # Process block
        block_data = await ingester.process_block(18500000)
        
        # Resolve entities
        entities = await er_pipeline.resolve_entities(block_data['transactions'])
        
        assert len(entities) > 0
        assert all('entity_id' in entity for entity in entities)
```

#### 3. E2E Tests
```python
# tests/e2e/test_comprehensive.py
import pytest
from fastapi.testclient import TestClient
from services.graph_api.graph_api import app

class TestEndToEnd:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_graphql_api(self, client):
        query = """
        query {
            entities(limit: 10) {
                id
                type
                addresses {
                    address
                }
            }
        }
        """
        
        response = client.post("/graphql", json={"query": query})
        assert response.status_code == 200
        
        data = response.json()
        assert 'data' in data
        assert 'entities' in data['data']
```

### Frontend Testing

#### 1. Component Tests
```tsx
// __tests__/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles correctly', () => {
    render(<Button variant="primary">Primary Button</Button>);
    const button = screen.getByText('Primary Button');
    expect(button).toHaveClass('chakra-button--primary');
  });
});
```

#### 2. Integration Tests
```tsx
// __tests__/integration/Dashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { Dashboard } from '../Dashboard';
import { GET_ENTITIES } from '../graphql/queries';

const mocks = [
  {
    request: {
      query: GET_ENTITIES,
      variables: { limit: 10 }
    },
    result: {
      data: {
        entities: [
          {
            id: '1',
            type: 'ADDRESS',
            addresses: [{ address: '0x123...' }]
          }
        ]
      }
    }
  }
];

describe('Dashboard Integration', () => {
  it('loads and displays entities', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <Dashboard />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('0x123...')).toBeInTheDocument();
    });
  });
});
```

#### 3. E2E Tests
```tsx
// __tests__/e2e/Dashboard.spec.ts
import { test, expect } from '@playwright/test';

test('dashboard loads and displays data', async ({ page }) => {
  await page.goto('/');
  
  // Wait for dashboard to load
  await page.waitForSelector('[data-testid="dashboard"]');
  
  // Check that entities are displayed
  const entityCards = await page.locator('[data-testid="entity-card"]');
  await expect(entityCards).toHaveCount(10);
  
  // Test search functionality
  await page.fill('[data-testid="search-input"]', '0x123');
  await page.click('[data-testid="search-button"]');
  
  // Verify search results
  await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
});
```

---

## Deployment and Production

### Backend Deployment

#### 1. Docker Configuration
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "services.graph_api.graph_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Kubernetes Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: onchain-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: onchain-api
  template:
    metadata:
      labels:
        app: onchain-api
    spec:
      containers:
      - name: api
        image: onchain-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

### Frontend Deployment

#### 1. Next.js Configuration
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['localhost'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_GRAPHQL_URL: process.env.NEXT_PUBLIC_GRAPHQL_URL,
  },
  experimental: {
    optimizeCss: true,
  },
}

module.exports = nextConfig
```

#### 2. Vercel Deployment
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "@api-url",
    "NEXT_PUBLIC_GRAPHQL_URL": "@graphql-url"
  }
}
```

---

This technical documentation provides a comprehensive guide for developing and maintaining the Onchain Command Center platform. It covers both backend and frontend architectures, integration patterns, performance optimization, testing strategies, and deployment procedures.

For additional details on specific components or services, refer to the individual service documentation in their respective directories. 