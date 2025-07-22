import React, { useState } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import Link from 'next/link';
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
  CardHeader,
  Divider,
  Badge,
  Button,
  useColorModeValue,
} from '@chakra-ui/react';
import { 
  ThemeProvider, 
  LayoutProvider, 
  useLayout,
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
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  const platformStats = [
    { label: 'Active Services', value: '15', icon: '⚡', color: 'blue' },
    { label: 'Data Sources', value: '8', icon: '📊', color: 'green' },
    { label: 'AI Models', value: '6', icon: '🤖', color: 'purple' },
    { label: 'Real-time Streams', value: '12', icon: '🔄', color: 'orange' },
  ];

  const quickActions = [
    {
      title: 'Explore Graph Network',
      description: 'Interactive blockchain network visualization',
      route: '/explorer',
      icon: '🌐',
      color: 'blue',
      status: 'active'
    },
    {
      title: 'Time Series Analysis',
      description: 'Real-time charts and analytics',
      route: '/canvas',
      icon: '📈',
      color: 'green',
      status: 'active'
    },
    {
      title: 'Compliance Dashboard',
      description: 'Regulatory compliance and risk mapping',
      route: '/compliance',
      icon: '🗺️',
      color: 'red',
      status: 'active'
    },
    {
      title: 'All Services',
      description: 'Browse complete service catalog',
      route: '/services',
      icon: '🏗️',
      color: 'purple',
      status: 'active'
    }
  ];

  const recentActivity = [
    { type: 'MEV Detection', message: 'Detected arbitrage opportunity on Uniswap', time: '2 min ago', status: 'alert' },
    { type: 'Entity Resolution', message: 'Resolved 147 new address clusters', time: '15 min ago', status: 'success' },
    { type: 'Risk Analysis', message: 'High-risk transaction flagged for review', time: '32 min ago', status: 'warning' },
    { type: 'Data Ingestion', message: 'Processed 1.2M transactions', time: '1 hour ago', status: 'info' }
  ];

  return (
    <ThemeProvider>
      <LayoutProvider>
        <Head>
          <title>Onchain Command Center | Blockchain Intelligence Platform</title>
          <meta name="description" content="Palantir-grade blockchain intelligence and analytics platform" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <Box minHeight="100vh" bg={bgColor}>
          {/* Header */}
          <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={4} shadow="sm">
            <Container maxW="7xl">
              <HStack justify="space-between" align="center">
                <VStack align="start" spacing={1}>
                  <Heading size="xl" bgGradient="linear(to-r, blue.500, purple.600)" bgClip="text">
                    Onchain Command Center
                  </Heading>
                  <Text color="gray.600">Palantir-grade Blockchain Intelligence Platform</Text>
                </VStack>
                <HStack spacing={3}>
                  <Badge colorScheme="green" variant="solid" px={3} py={1}>
                    OPERATIONAL
                  </Badge>
                  <Text fontSize="sm" color="gray.500">
                    Last updated: {new Date().toLocaleTimeString()}
                  </Text>
                </HStack>
              </HStack>
            </Container>
          </Box>

          {/* Main Dashboard */}
          <Container maxW="7xl" py={8}>
            <VStack spacing={8} align="stretch">
              
              {/* Platform Stats */}
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
                {platformStats.map((stat, idx) => (
                  <Card key={idx} bg={cardBg} shadow="md">
                    <CardBody>
                      <HStack justify="space-between" align="center">
                        <VStack align="start" spacing={1}>
                          <Text fontSize="2xl" fontWeight="bold" color={`${stat.color}.500`}>
                            {stat.value}
                          </Text>
                          <Text fontSize="sm" color="gray.600">
                            {stat.label}
                          </Text>
                        </VStack>
                        <Text fontSize="2xl">{stat.icon}</Text>
                      </HStack>
                    </CardBody>
                  </Card>
                ))}
              </SimpleGrid>

              <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={8}>
                {/* Quick Actions */}
                <Box gridColumn={{ lg: 'span 2' }}>
                  <Card bg={cardBg} shadow="md">
                    <CardHeader>
                      <Heading size="md">Quick Actions</Heading>
                      <Text fontSize="sm" color="gray.600">
                        Access key platform capabilities
                      </Text>
                    </CardHeader>
                    <CardBody pt={0}>
                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                        {quickActions.map((action, idx) => (
                          <Link key={idx} href={action.route}>
                            <Card 
                              bg={`${action.color}.50`} 
                              border="1px solid" 
                              borderColor={`${action.color}.100`}
                              cursor="pointer"
                              _hover={{ 
                                transform: 'translateY(-2px)', 
                                shadow: 'lg',
                                borderColor: `${action.color}.200`
                              }}
                              transition="all 0.2s"
                            >
                              <CardBody p={4}>
                                <HStack spacing={3}>
                                  <Text fontSize="xl">{action.icon}</Text>
                                  <VStack align="start" spacing={1} flex={1}>
                                    <HStack justify="space-between" width="100%">
                                      <Text fontWeight="semibold" fontSize="sm">
                                        {action.title}
                                      </Text>
                                      <Badge 
                                        colorScheme={action.status === 'active' ? 'green' : 'gray'} 
                                        size="sm"
                                      >
                                        {action.status}
                                      </Badge>
                                    </HStack>
                                    <Text fontSize="xs" color="gray.600">
                                      {action.description}
                                    </Text>
                                  </VStack>
                                </HStack>
                              </CardBody>
                            </Card>
                          </Link>
                        ))}
                      </SimpleGrid>
                    </CardBody>
                  </Card>
                </Box>

                {/* Recent Activity */}
                <Card bg={cardBg} shadow="md">
                  <CardHeader>
                    <Heading size="md">Recent Activity</Heading>
                    <Text fontSize="sm" color="gray.600">
                      System events and alerts
                    </Text>
                  </CardHeader>
                  <CardBody pt={0}>
                    <VStack spacing={3} align="stretch">
                      {recentActivity.map((activity, idx) => (
                        <Box key={idx} p={3} bg="gray.50" rounded="md">
                          <HStack justify="space-between" align="start">
                            <VStack align="start" spacing={1} flex={1}>
                              <HStack>
                                <Badge 
                                  colorScheme={
                                    activity.status === 'alert' ? 'red' :
                                    activity.status === 'success' ? 'green' :
                                    activity.status === 'warning' ? 'yellow' : 'blue'
                                  } 
                                  size="sm"
                                >
                                  {activity.type}
                                </Badge>
                              </HStack>
                              <Text fontSize="xs" noOfLines={2}>
                                {activity.message}
                              </Text>
                              <Text fontSize="xs" color="gray.500">
                                {activity.time}
                              </Text>
                            </VStack>
                          </HStack>
                        </Box>
                      ))}
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>

              {/* System Architecture Overview */}
              <Card bg={cardBg} shadow="md">
                <CardHeader>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <Heading size="md">Platform Architecture</Heading>
                      <Text fontSize="sm" color="gray.600">
                        7-layer Palantir-grade architecture
                      </Text>
                    </VStack>
                    <Link href="/services">
                      <Button variant="outline" size="sm">
                        View All Services
                      </Button>
                    </Link>
                  </HStack>
                </CardHeader>
                <CardBody pt={0}>
                  <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
                    {[
                      { layer: 'Identity & Access', services: ['Access Control', 'Audit Logs'], icon: '🔐' },
                      { layer: 'Ingestion', services: ['Ethereum Ingester', 'Real-time Streams'], icon: '📥' },
                      { layer: 'Intelligence', services: ['AI Models', 'Agent Mesh'], icon: '🧠' },
                      { layer: 'Visualization', services: ['Graph Explorer', 'Time Series'], icon: '📊' }
                    ].map((arch, idx) => (
                      <VStack key={idx} spacing={2} p={3} bg="gray.50" rounded="md">
                        <Text fontSize="2xl">{arch.icon}</Text>
                        <Text fontWeight="semibold" fontSize="sm" textAlign="center">
                          {arch.layer}
                        </Text>
                        <VStack spacing={1}>
                          {arch.services.map((service, sidx) => (
                            <Text key={sidx} fontSize="xs" color="gray.600" textAlign="center">
                              {service}
                            </Text>
                          ))}
                        </VStack>
                      </VStack>
                    ))}
                  </SimpleGrid>
                </CardBody>
              </Card>

            </VStack>
          </Container>
        </Box>
      </LayoutProvider>
    </ThemeProvider>
  );
};

export default Home;
