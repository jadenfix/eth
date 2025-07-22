import React, { useState } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  Divider,
} from '@chakra-ui/react';
import { 
  ThemeProvider, 
  LayoutProvider, 
  useLayout,
  Button,
  Icon,
  Spinner,
  NavBar,
  SideBar,
  DockableLayout,
  GraphExplorer,
  GraphData,
  PanelConfig,
} from '../src/components';

// Mock data for the graph explorer
const mockGraphData: GraphData = {
  nodes: [
    {
      id: 'addr1',
      label: '0x742d35Cc6634C0532925a3b8D6Ac492395d8',
      type: 'address',
      value: 1000,
      riskScore: 25,
      balance: 150.5,
      txCount: 245,
      x: 100,
      y: 100,
      size: 15,
      color: '#4299E1',
    },
    {
      id: 'addr2',
      label: '0x8ba1f109551bD432803012645Hac136c82',
      type: 'address',
      value: 500,
      riskScore: 85,
      balance: 23.2,
      txCount: 1200,
      x: 300,
      y: 150,
      size: 20,
      color: '#F56565',
    },
    {
      id: 'contract1',
      label: 'Uniswap V3 Router',
      type: 'contract',
      value: 2000,
      riskScore: 10,
      balance: 0,
      txCount: 50000,
      x: 200,
      y: 250,
      size: 25,
      color: '#38B2AC',
    },
  ],
  edges: [
    {
      id: 'edge1',
      source: 'addr1',
      target: 'contract1',
      type: 'transfer',
      value: 50.5,
      timestamp: Date.now() - 3600000,
      txHash: '0xabc123...',
      weight: 3,
      color: '#A0AEC0',
      width: 2,
    },
    {
      id: 'edge2',
      source: 'contract1',
      target: 'addr2',
      type: 'transfer',
      value: 25.0,
      timestamp: Date.now() - 1800000,
      txHash: '0xdef456...',
      weight: 2,
      color: '#A0AEC0',
      width: 1.5,
    },
  ],
};

// Sample panel configurations
const samplePanels: PanelConfig[] = [
  {
    id: 'graph-explorer-1',
    type: 'graph-explorer',
    title: 'Address Network',
    subtitle: 'Transaction flow analysis',
    component: GraphExplorer,
    props: { data: mockGraphData },
    position: { x: 50, y: 50, width: 800, height: 600 },
    isDraggable: true,
    isResizable: true,
    zIndex: 1,
  },
];

// Demo sections component
const ComponentDemo: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const mockUser = {
    name: 'John Analyst',
    email: 'john@palantir.com',
    role: 'Senior Investigator',
    avatar: undefined,
  };

  const sidebarItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'chart' as const,
      isActive: true,
      count: 5,
    },
    {
      id: 'explorer',
      label: 'Network Explorer',
      icon: 'graph' as const,
      count: 2,
    },
    {
      id: 'investigations',
      label: 'Investigations',
      icon: 'search' as const,
      isCollapsible: true,
      children: [
        {
          id: 'active-cases',
          label: 'Active Cases',
          icon: 'flag' as const,
          count: 3,
        },
        {
          id: 'closed-cases',
          label: 'Closed Cases',
          icon: 'check' as const,
          count: 15,
        },
      ],
    },
    {
      id: 'compliance',
      label: 'Compliance',
      icon: 'shield' as const,
      badge: { text: 'New', color: 'red' },
    },
    {
      id: 'reports',
      label: 'Reports',
      icon: 'table' as const,
    },
  ];

  return (
    <VStack spacing={8} align="stretch">
      {/* Atoms Demo */}
      <Box>
        <Heading size="lg" mb={4}>Atomic Components</Heading>
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
          {/* Buttons */}
          <Card>
            <CardBody>
              <Text fontWeight="bold" mb={3}>Buttons</Text>
              <VStack spacing={2} align="stretch">
                <Button variant="primary" size="sm">Primary</Button>
                <Button variant="secondary" size="sm">Secondary</Button>
                <Button variant="outline" size="sm">Outline</Button>
                <Button variant="ghost" size="sm">Ghost</Button>
                <Button variant="danger" size="sm">Danger</Button>
              </VStack>
            </CardBody>
          </Card>

          {/* Icons */}
          <Card>
            <CardBody>
              <Text fontWeight="bold" mb={3}>Icons</Text>
              <SimpleGrid columns={4} spacing={2}>
                <Icon name="search" size="md" />
                <Icon name="user" size="md" />
                <Icon name="settings" size="md" />
                <Icon name="graph" size="md" />
                <Icon name="shield" size="md" />
                <Icon name="transaction" size="md" />
                <Icon name="wallet" size="md" />
                <Icon name="flag" size="md" />
              </SimpleGrid>
            </CardBody>
          </Card>

          {/* Spinners */}
          <Card>
            <CardBody>
              <Text fontWeight="bold" mb={3}>Loading States</Text>
              <VStack spacing={3}>
                <Spinner variant="default" size="md" />
                <Spinner variant="dots" size="md" />
                <Spinner variant="pulse" size="md" />
                <Spinner variant="ring" size="md" />
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>
      </Box>

      <Divider />

      {/* Molecules Demo */}
      <Box>
        <Heading size="lg" mb={4}>Molecular Components</Heading>
        <VStack spacing={6} align="stretch">
          {/* Navigation Bar */}
          <Card>
            <CardBody p={0}>
              <Text fontWeight="bold" p={4} pb={0}>Navigation Bar</Text>
              <Box border="1px solid" borderColor="gray.200" borderRadius="md" mt={3}>
                <NavBar
                  user={mockUser}
                  notifications={3}
                  isLoading={isLoading}
                  onSearch={(query) => console.log('Search:', query)}
                  onNotificationsClick={() => console.log('Notifications clicked')}
                  onSettingsClick={() => console.log('Settings clicked')}
                  onLogout={() => console.log('Logout clicked')}
                />
              </Box>
            </CardBody>
          </Card>

          {/* Sidebar */}
          <Card>
            <CardBody p={0}>
              <Text fontWeight="bold" p={4} pb={0}>Sidebar Navigation</Text>
              <Box height="400px" border="1px solid" borderColor="gray.200" borderRadius="md" mt={3} overflow="hidden">
                <SideBar
                  items={sidebarItems}
                  onItemClick={(item) => console.log('Sidebar item clicked:', item)}
                />
              </Box>
            </CardBody>
          </Card>
        </VStack>
      </Box>

      <Divider />

      {/* Organisms Demo */}
      <Box>
        <Heading size="lg" mb={4}>Organism Components</Heading>
        <Card>
          <CardBody>
            <Text fontWeight="bold" mb={3}>Graph Explorer</Text>
            <Box height="500px" border="1px solid" borderColor="gray.200" borderRadius="md" overflow="hidden">
              <GraphExplorer
                data={mockGraphData}
                width={800}
                height={500}
                onNodeClick={(node) => console.log('Node clicked:', node)}
                onEdgeClick={(edge) => console.log('Edge clicked:', edge)}
              />
            </Box>
          </CardBody>
        </Card>
      </Box>
    </VStack>
  );
};

// Main workspace demo
const WorkspaceDemo: React.FC = () => {
  const { state, addPanel, updatePanel, removePanel } = useLayout();

  React.useEffect(() => {
    // Add initial panels if none exist
    if (state.panels.length === 0) {
      samplePanels.forEach(panel => {
        const { id, ...panelData } = panel;
        addPanel(panelData);
      });
    }
  }, [state.panels.length, addPanel]);

  return (
    <Box height="100vh" overflow="hidden">
      <DockableLayout
        panels={state.panels}
        onPanelUpdate={updatePanel}
        onPanelClose={removePanel}
        gridSize={state.gridSize}
        snapToGrid={state.snapToGrid}
        showGrid={state.isGridVisible}
      />
    </Box>
  );
};

// Main page component
const Home: NextPage = () => {
  type TabType = 'components' | 'workspace';
  const [activeTab, setActiveTab] = useState<TabType>('components');

  return (
    <ThemeProvider>
      <LayoutProvider>
        <Head>
          <title>Palantir Intelligence - Atomic Design System</title>
          <meta name="description" content="Blockchain intelligence platform with atomic design components" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <Box minHeight="100vh" bg="gray.50">
          {activeTab === 'components' ? (
            <>
              {/* Header */}
              <Box bg="white" borderBottom="1px solid" borderColor="gray.200" py={4}>
                <Container maxW="7xl">
                  <HStack justify="space-between" align="center">
                    <VStack align="start" spacing={1}>
                      <Heading size="xl" color="blue.600">
                        Palantir Intelligence
                      </Heading>
                      <Text color="gray.600">Atomic Design System Demo</Text>
                    </VStack>
                    <HStack spacing={2}>
                      <Button
                        variant={activeTab === 'components' ? 'primary' : 'outline'}
                        onClick={() => setActiveTab('components')}
                        size="sm"
                      >
                        Components
                      </Button>
                      <Button
                        variant={activeTab === 'workspace' ? 'primary' : 'outline'}
                        onClick={() => setActiveTab('workspace')}
                        size="sm"
                      >
                        Workspace
                      </Button>
                    </HStack>
                  </HStack>
                </Container>
              </Box>

              {/* Main Content */}
              <Container maxW="7xl" py={8}>
                <ComponentDemo />
              </Container>
            </>
          ) : (
            <WorkspaceDemo />
          )}
        </Box>
      </LayoutProvider>
    </ThemeProvider>
  );
};

export default Home;
