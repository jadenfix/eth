# Frontend Development Guide

## Overview

This guide provides comprehensive instructions for developing and extending the Onchain Command Center frontend. The frontend is built with Next.js 14, TypeScript, and Chakra UI, following atomic design principles and Palantir-style workspace management.

## Quick Start

### Prerequisites
- Node.js 18+
- npm 9+
- Git

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd eth

# Install frontend dependencies
cd services/ui/nextjs-app
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

## Architecture Overview

### Current Structure
```
services/ui/nextjs-app/
├── src/
│   ├── components/
│   │   ├── atoms/          # Basic UI elements (Button, Icon, Spinner)
│   │   ├── molecules/      # Compound components (NavBar, SideBar)
│   │   ├── organisms/      # Complex components (Dashboard, GraphExplorer)
│   │   └── layout/         # Layout components (EnhancedLayout, SideRail)
│   ├── pages/              # Next.js pages (index, explorer, analytics, etc.)
│   ├── theme/              # Design system (colors, typography, motion)
│   ├── providers/          # Context providers (ThemeProvider, LayoutProvider)
│   └── lib/                # Utilities and helpers
├── public/                 # Static assets
└── styles/                 # Global styles
```

### Design System

The frontend uses a comprehensive design system with:

- **Color Palette**: Semantic colors for risk levels, entity types, and UI states
- **Typography**: Inter for UI, JetBrains Mono for code
- **Spacing**: Consistent 8px grid system
- **Motion**: Framer Motion for animations and transitions

## Component Development

### Creating New Components

#### 1. Atom Component Example
```tsx
// src/components/atoms/Badge.tsx
import React from 'react';
import { Badge as ChakraBadge, BadgeProps } from '@chakra-ui/react';

interface BadgeProps extends BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'info', 
  size = 'md',
  ...props 
}) => {
  const variantStyles = {
    success: { bg: 'green.100', color: 'green.800' },
    warning: { bg: 'yellow.100', color: 'yellow.800' },
    error: { bg: 'red.100', color: 'red.800' },
    info: { bg: 'blue.100', color: 'blue.800' }
  };

  const sizeStyles = {
    sm: { px: 2, py: 1, fontSize: 'xs' },
    md: { px: 3, py: 1, fontSize: 'sm' },
    lg: { px: 4, py: 2, fontSize: 'md' }
  };

  return (
    <ChakraBadge
      {...variantStyles[variant]}
      {...sizeStyles[size]}
      borderRadius="full"
      fontWeight="medium"
      {...props}
    >
      {children}
    </ChakraBadge>
  );
};
```

#### 2. Molecule Component Example
```tsx
// src/components/molecules/DataCard.tsx
import React from 'react';
import { Box, Text, Badge, Flex, Icon } from '@chakra-ui/react';

interface DataCardProps {
  title: string;
  value: string | number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon?: string;
  variant?: 'default' | 'highlight' | 'muted';
}

export const DataCard: React.FC<DataCardProps> = ({
  title,
  value,
  change,
  trend = 'neutral',
  icon,
  variant = 'default'
}) => {
  const variantStyles = {
    default: { bg: 'white', border: '1px solid', borderColor: 'gray.200' },
    highlight: { bg: 'blue.50', border: '1px solid', borderColor: 'blue.200' },
    muted: { bg: 'gray.50', border: '1px solid', borderColor: 'gray.100' }
  };

  const trendColors = {
    up: 'green.500',
    down: 'red.500',
    neutral: 'gray.500'
  };

  return (
    <Box
      p={4}
      borderRadius="lg"
      boxShadow="sm"
      {...variantStyles[variant]}
    >
      <Flex justify="space-between" align="center" mb={2}>
        <Text fontSize="sm" color="gray.600" fontWeight="medium">
          {title}
        </Text>
        {icon && <Icon name={icon} color="gray.400" />}
      </Flex>
      
      <Text fontSize="2xl" fontWeight="bold" mb={1}>
        {value}
      </Text>
      
      {change !== undefined && (
        <Flex align="center" gap={1}>
          <Icon 
            name={trend === 'up' ? 'arrow-up' : 'arrow-down'} 
            color={trendColors[trend]}
            size="sm"
          />
          <Text fontSize="sm" color={trendColors[trend]}>
            {Math.abs(change)}%
          </Text>
        </Flex>
      )}
    </Box>
  );
};
```

#### 3. Organism Component Example
```tsx
// src/components/organisms/TransactionTable.tsx
import React, { useState, useMemo } from 'react';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Box,
  Text,
  Badge,
  Flex,
  Button,
  Input,
  Select
} from '@chakra-ui/react';

interface Transaction {
  id: string;
  hash: string;
  from: string;
  to: string;
  value: string;
  gasUsed: number;
  status: 'success' | 'failed';
  timestamp: number;
}

interface TransactionTableProps {
  transactions: Transaction[];
  onTransactionClick?: (transaction: Transaction) => void;
  loading?: boolean;
}

export const TransactionTable: React.FC<TransactionTableProps> = ({
  transactions,
  onTransactionClick,
  loading = false
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<keyof Transaction>('timestamp');

  const filteredTransactions = useMemo(() => {
    return transactions
      .filter(tx => {
        const matchesSearch = 
          tx.hash.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tx.from.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tx.to.toLowerCase().includes(searchTerm.toLowerCase());
        
        const matchesStatus = statusFilter === 'all' || tx.status === statusFilter;
        
        return matchesSearch && matchesStatus;
      })
      .sort((a, b) => {
        if (sortBy === 'timestamp') {
          return b.timestamp - a.timestamp;
        }
        return String(a[sortBy]).localeCompare(String(b[sortBy]));
      });
  }, [transactions, searchTerm, statusFilter, sortBy]);

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatValue = (value: string) => {
    const ethValue = parseFloat(value) / 1e18;
    return `${ethValue.toFixed(4)} ETH`;
  };

  return (
    <Box>
      <Flex gap={4} mb={4}>
        <Input
          placeholder="Search transactions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          maxW="300px"
        />
        <Select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          maxW="150px"
        >
          <option value="all">All Status</option>
          <option value="success">Success</option>
          <option value="failed">Failed</option>
        </Select>
      </Flex>

      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Hash</Th>
            <Th>From</Th>
            <Th>To</Th>
            <Th>Value</Th>
            <Th>Gas Used</Th>
            <Th>Status</Th>
            <Th>Time</Th>
          </Tr>
        </Thead>
        <Tbody>
          {filteredTransactions.map((tx) => (
            <Tr 
              key={tx.id}
              cursor="pointer"
              _hover={{ bg: 'gray.50' }}
              onClick={() => onTransactionClick?.(tx)}
            >
              <Td>
                <Text fontFamily="mono" fontSize="sm">
                  {formatAddress(tx.hash)}
                </Text>
              </Td>
              <Td>
                <Text fontFamily="mono" fontSize="sm">
                  {formatAddress(tx.from)}
                </Text>
              </Td>
              <Td>
                <Text fontFamily="mono" fontSize="sm">
                  {formatAddress(tx.to)}
                </Text>
              </Td>
              <Td>
                <Text fontWeight="medium">
                  {formatValue(tx.value)}
                </Text>
              </Td>
              <Td>{tx.gasUsed.toLocaleString()}</Td>
              <Td>
                <Badge
                  colorScheme={tx.status === 'success' ? 'green' : 'red'}
                  variant="subtle"
                >
                  {tx.status}
                </Badge>
              </Td>
              <Td>
                <Text fontSize="sm" color="gray.600">
                  {new Date(tx.timestamp * 1000).toLocaleTimeString()}
                </Text>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};
```

## Page Development

### Creating New Pages

#### 1. Basic Page Structure
```tsx
// pages/new-feature.tsx
import React from 'react';
import { Box, Heading, Text } from '@chakra-ui/react';
import { Layout } from '@/components/layout/EnhancedLayout';

export default function NewFeaturePage() {
  return (
    <Layout>
      <Box p={6}>
        <Heading size="lg" mb={4}>
          New Feature
        </Heading>
        <Text>
          This is a new feature page with the standard layout.
        </Text>
      </Box>
    </Layout>
  );
}
```

#### 2. Page with Data Fetching
```tsx
// pages/entity/[id].tsx
import React from 'react';
import { useRouter } from 'next/router';
import { Box, Heading, Spinner, Alert, AlertIcon } from '@chakra-ui/react';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';
import { Layout } from '@/components/layout/EnhancedLayout';
import { EntityDetails } from '@/components/organisms/EntityDetails';

const GET_ENTITY = gql`
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
    }
  }
`;

export default function EntityPage() {
  const router = useRouter();
  const { id } = router.query;

  const { loading, error, data } = useQuery(GET_ENTITY, {
    variables: { id },
    skip: !id
  });

  if (loading) {
    return (
      <Layout>
        <Box display="flex" justify="center" align="center" h="400px">
          <Spinner size="xl" />
        </Box>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Box p={6}>
          <Alert status="error">
            <AlertIcon />
            Error loading entity: {error.message}
          </Alert>
        </Box>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box p={6}>
        <EntityDetails entity={data.entity} />
      </Box>
    </Layout>
  );
}
```

## State Management

### Using React Context

#### 1. Creating a Context
```tsx
// src/providers/EntityProvider.tsx
import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface Entity {
  id: string;
  type: string;
  addresses: string[];
}

interface EntityState {
  selectedEntity: Entity | null;
  entities: Entity[];
  loading: boolean;
}

type EntityAction =
  | { type: 'SET_SELECTED_ENTITY'; payload: Entity | null }
  | { type: 'SET_ENTITIES'; payload: Entity[] }
  | { type: 'SET_LOADING'; payload: boolean };

const EntityContext = createContext<{
  state: EntityState;
  dispatch: React.Dispatch<EntityAction>;
} | undefined>(undefined);

const entityReducer = (state: EntityState, action: EntityAction): EntityState => {
  switch (action.type) {
    case 'SET_SELECTED_ENTITY':
      return { ...state, selectedEntity: action.payload };
    case 'SET_ENTITIES':
      return { ...state, entities: action.payload };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
};

const initialState: EntityState = {
  selectedEntity: null,
  entities: [],
  loading: false
};

export const EntityProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(entityReducer, initialState);

  return (
    <EntityContext.Provider value={{ state, dispatch }}>
      {children}
    </EntityContext.Provider>
  );
};

export const useEntity = () => {
  const context = useContext(EntityContext);
  if (context === undefined) {
    throw new Error('useEntity must be used within an EntityProvider');
  }
  return context;
};
```

#### 2. Using the Context
```tsx
// In a component
import { useEntity } from '@/providers/EntityProvider';

const MyComponent = () => {
  const { state, dispatch } = useEntity();

  const handleEntitySelect = (entity: Entity) => {
    dispatch({ type: 'SET_SELECTED_ENTITY', payload: entity });
  };

  return (
    <div>
      {state.selectedEntity && (
        <Text>Selected: {state.selectedEntity.id}</Text>
      )}
    </div>
  );
};
```

## API Integration

### GraphQL Integration

#### 1. Setting up Apollo Client
```tsx
// src/lib/apollo.ts
import { ApolloClient, InMemoryCache, createHttpLink } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';

const httpLink = createHttpLink({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_URL || 'http://localhost:8000/graphql',
});

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('authToken');
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : "",
    }
  };
});

export const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
```

#### 2. Creating Custom Hooks
```tsx
// src/hooks/useEntities.ts
import { useQuery, useMutation, gql } from '@apollo/client';

const GET_ENTITIES = gql`
  query GetEntities($limit: Int, $offset: Int) {
    entities(limit: $limit, offset: $offset) {
      id
      type
      addresses {
        address
        label
      }
    }
  }
`;

const CREATE_ENTITY = gql`
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
`;

export const useEntities = (limit: number = 10, offset: number = 0) => {
  return useQuery(GET_ENTITIES, {
    variables: { limit, offset },
    pollInterval: 5000, // Refresh every 5 seconds
  });
};

export const useCreateEntity = () => {
  return useMutation(CREATE_ENTITY, {
    refetchQueries: [{ query: GET_ENTITIES }],
  });
};
```

### REST API Integration

#### 1. API Client
```tsx
// src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const token = localStorage.getItem('authToken');

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient(API_BASE);
```

#### 2. Using the API Client
```tsx
// src/hooks/useApi.ts
import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = useCallback(async <T>(
    method: keyof typeof apiClient,
    endpoint: string,
    data?: any
  ): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiClient[method](endpoint, data);
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { loading, error, request };
};
```

## Visualization Components

### Network Graph Component
```tsx
// src/components/visualizations/NetworkGraph.tsx
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface Node {
  id: string;
  label: string;
  type: 'address' | 'contract' | 'token';
  value: number;
}

interface Link {
  source: string;
  target: string;
  value: number;
}

interface NetworkGraphProps {
  nodes: Node[];
  links: Link[];
  width: number;
  height: number;
  onNodeClick?: (node: Node) => void;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  nodes,
  links,
  width,
  height,
  onNodeClick
}) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.value));

    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', (d: any) => Math.sqrt(d.value) + 5)
      .attr('fill', (d: any) => {
        switch (d.type) {
          case 'address': return '#3B82F6';
          case 'contract': return '#8B5CF6';
          case 'token': return '#10B981';
          default: return '#6B7280';
        }
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (event, d) => onNodeClick?.(d));

    const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text((d: any) => d.label)
      .attr('font-size', '12px')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('fill', '#374151');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y);

      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y);
    });

    return () => simulation.stop();
  }, [nodes, links, width, height, onNodeClick]);

  return (
    <svg ref={svgRef} width={width} height={height}>
      <g />
    </svg>
  );
};
```

### Time Series Chart Component
```tsx
// src/components/visualizations/TimeSeriesChart.tsx
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

interface DataPoint {
  timestamp: number;
  value: number;
  label: string;
}

interface TimeSeriesChartProps {
  data: DataPoint[];
  title: string;
  color?: string;
  height?: number;
}

export const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
  data,
  title,
  color = '#3182CE',
  height = 300
}) => {
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div style={{ width: '100%', height }}>
      <h3 style={{ marginBottom: '16px', fontSize: '18px', fontWeight: 'bold' }}>
        {title}
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatTimestamp}
            fontSize={12}
          />
          <YAxis fontSize={12} />
          <Tooltip
            labelFormatter={formatTimestamp}
            formatter={(value: number) => [value, 'Value']}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={{ fill: color, strokeWidth: 2, r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
```

## Testing

### Component Testing
```tsx
// __tests__/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/atoms/Button';

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

  it('disables button when loading', () => {
    render(<Button loading>Loading Button</Button>);
    const button = screen.getByText('Loading Button');
    expect(button).toBeDisabled();
  });
});
```

### Page Testing
```tsx
// __tests__/pages/index.test.tsx
import { render, screen } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import HomePage from '@/pages/index';

const mocks = [
  {
    request: {
      query: GET_DASHBOARD_DATA,
      variables: {}
    },
    result: {
      data: {
        dashboard: {
          totalTransactions: 1000,
          activeEntities: 50,
          recentSignals: []
        }
      }
    }
  }
];

describe('HomePage', () => {
  it('renders dashboard components', () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <HomePage />
      </MockedProvider>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Total Transactions')).toBeInTheDocument();
  });
});
```

## Performance Optimization

### Code Splitting
```tsx
// Dynamic imports for heavy components
import dynamic from 'next/dynamic';

const GraphExplorer = dynamic(() => import('@/components/GraphExplorer'), {
  loading: () => <Spinner />,
  ssr: false
});

const AnalyticsDashboard = dynamic(() => import('@/components/AnalyticsDashboard'), {
  loading: () => <Spinner />,
  ssr: false
});
```

### Memoization
```tsx
// Memoized components and calculations
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

### Virtualization
```tsx
// Virtualized list for large datasets
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

## Deployment

### Environment Configuration
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GRAPHQL_URL=http://localhost:8000/graphql
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Build and Deploy
```bash
# Build for production
npm run build

# Start production server
npm run start

# Deploy to Vercel
vercel --prod
```

## Best Practices

### 1. Component Structure
- Use atomic design principles
- Keep components focused and single-purpose
- Use TypeScript for type safety
- Include comprehensive prop types

### 2. State Management
- Use React Context for global state
- Keep local state in components when possible
- Use custom hooks for reusable logic

### 3. Performance
- Implement code splitting for large components
- Use memoization for expensive calculations
- Optimize re-renders with React.memo
- Use virtualization for large lists

### 4. Testing
- Write tests for all components
- Use React Testing Library for component tests
- Mock external dependencies
- Test user interactions and edge cases

### 5. Accessibility
- Use semantic HTML elements
- Include ARIA labels and descriptions
- Ensure keyboard navigation works
- Test with screen readers

This guide provides a comprehensive foundation for developing and extending the Onchain Command Center frontend. For additional details on specific components or features, refer to the individual component documentation and the main technical documentation. 