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
  Button,
  useColorModeValue,
  SimpleGrid,
  Card,
  CardBody,
  Badge,
  Icon,
} from '@chakra-ui/react';
import { 
  ThemeProvider,
  DockableLayout,
  GraphExplorer,
} from '../components';
import { PanelConfig, PanelType } from '../components/organisms/DockableLayout';

// Define GraphData interface locally
interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    value: number;
    riskScore: number;
    balance: number;
    txCount: number;
    x: number;
    y: number;
    size: number;
    color: string;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    type: string;
    value: number;
    timestamp: number;
    color: string;
    width: number;
  }>;
}

// Mock data for workspace demonstration
const mockGraphData: GraphData = {
  nodes: [
    {
      id: 'addr1',
      label: '0x742d35Cc...',
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
      label: '0x8ba1f109...',
      type: 'address',
      value: 800,
      riskScore: 75,
      balance: 89.2,
      txCount: 132,
      x: 250,
      y: 150,
      size: 12,
      color: '#F56565',
    },
    {
      id: 'contract1',
      label: 'Uniswap V3',
      type: 'contract',
      value: 5000,
      riskScore: 10,
      balance: 2500.8,
      txCount: 10000,
      x: 175,
      y: 250,
      size: 20,
      color: '#48BB78',
    },
  ],
  edges: [
    {
      id: 'edge1',
      source: 'addr1',
      target: 'addr2',
      type: 'transfer',
      value: 100,
      timestamp: 1640995200,
      color: '#A0AEC0',
      width: 2,
    },
    {
      id: 'edge2',
      source: 'addr1',
      target: 'contract1',
      type: 'contract_call',
      value: 50,
      timestamp: 1640995300,
      color: '#A0AEC0',
      width: 1.5,
    },
  ],
};

const WorkspacePage: NextPage = () => {
  const [panels, setPanels] = useState<PanelConfig[]>([
    {
      id: 'graph-explorer-1',
      type: 'graph-explorer',
      title: 'Transaction Network',
      subtitle: 'Interactive address relationships',
      component: GraphExplorer,
      props: { data: mockGraphData },
      position: { x: 50, y: 50, width: 800, height: 600 },
      isDraggable: true,
      isResizable: true,
      zIndex: 1,
    }
  ]);

  const bgColor = useColorModeValue('gray.100', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  const availableWidgets = [
    { id: 'graph-explorer', name: 'Network Graph', icon: '🌐', description: 'Interactive network visualization' },
    { id: 'timeseries-chart', name: 'Time Series', icon: '📊', description: 'Historical data charts' },
    { id: 'compliance-map', name: 'Risk Monitor', icon: '⚠️', description: 'Real-time risk assessment' },
    { id: 'data-table', name: 'TX Stream', icon: '💱', description: 'Live transaction feed' },
    { id: 'code-console', name: 'Analytics', icon: '📈', description: 'Statistical analysis' },
    { id: 'workspace-builder', name: 'Alert Center', icon: '🔔', description: 'System notifications' },
  ];

  const addPanel = (widgetType: string) => {
    // Map widget types to valid PanelTypes
    const typeMap: Record<string, PanelType> = {
      'graph-explorer': 'graph-explorer',
      'timeseries-chart': 'timeseries-chart', 
      'compliance-map': 'compliance-map',
      'data-table': 'data-table',
      'code-console': 'code-console',
      'workspace-builder': 'workspace-builder',
    };
    
    const panelType = typeMap[widgetType] || 'custom';
    const newPanel: PanelConfig = {
      id: `${widgetType}-${Date.now()}`,
      type: panelType,
      title: availableWidgets.find(w => w.id === widgetType)?.name || 'New Panel',
      subtitle: 'Drag and resize me!',
      component: GraphExplorer, // Placeholder - in real app would be dynamic
      props: { data: mockGraphData },
      position: { 
        x: Math.random() * 200, 
        y: Math.random() * 200, 
        width: 400, 
        height: 300 
      },
      isDraggable: true,
      isResizable: true,
      zIndex: panels.length + 1,
    };
    setPanels([...panels, newPanel]);
  };

  return (
    <ThemeProvider>
      <Box bg={bgColor} minH="100vh">
        <Head>
          <title>Workspace | Onchain Command Center</title>
          <meta name="description" content="Foundry-style customizable workspace for blockchain intelligence" />
        </Head>

        {/* Header */}
        <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={3} shadow="sm">
          <Container maxW="7xl" px={6}>
            <HStack justify="space-between" align="center">
              <HStack spacing={4}>
                <Link href="/">
                  <Button variant="ghost" size="sm">← Back</Button>
                </Link>
                <Text fontSize="xl">🏗️</Text>
                <VStack align="start" spacing={0}>
                  <Heading size="md">Foundry Workspace</Heading>
                  <Text fontSize="sm" color="gray.600">Drag, drop, and customize your dashboard</Text>
                </VStack>
              </HStack>

              <HStack spacing={3}>
                <Badge colorScheme="blue" variant="solid" px={3} py={1}>
                  {panels.length} PANELS
                </Badge>
                <Link href="/services">
                  <Button variant="outline" size="sm">All Services</Button>
                </Link>
              </HStack>
            </HStack>
          </Container>
        </Box>

        {/* Sidebar with Available Widgets */}
        <HStack align="stretch" spacing={0} h="calc(100vh - 80px)">
          <Box bg={cardBg} w="300px" borderRight="1px solid" borderColor="gray.200" p={4}>
            <VStack spacing={4} align="stretch">
              <Heading size="sm">Available Widgets</Heading>
              <Text fontSize="xs" color="gray.600">
                Click to add widgets to your workspace
              </Text>
              
              <VStack spacing={2} align="stretch">
                {availableWidgets.map((widget) => (
                  <Card
                    key={widget.id}
                    size="sm"
                    cursor="pointer"
                    _hover={{ bg: 'gray.50', transform: 'translateY(-1px)' }}
                    transition="all 0.2s"
                    onClick={() => addPanel(widget.id)}
                  >
                    <CardBody p={3}>
                      <HStack spacing={3}>
                        <Text fontSize="lg">{widget.icon}</Text>
                        <VStack align="start" spacing={0} flex={1}>
                          <Text fontWeight="medium" fontSize="sm">
                            {widget.name}
                          </Text>
                          <Text fontSize="xs" color="gray.600" noOfLines={2}>
                            {widget.description}
                          </Text>
                        </VStack>
                      </HStack>
                    </CardBody>
                  </Card>
                ))}
              </VStack>

              <Box pt={4}>
                <Text fontSize="xs" color="gray.500" mb={2}>Quick Actions:</Text>
                <VStack spacing={2} align="stretch">
                  <Button size="xs" variant="outline" onClick={() => setPanels([])}>
                    Clear All Panels
                  </Button>
                  <Button size="xs" variant="outline" isDisabled>
                    Save Layout
                  </Button>
                  <Button size="xs" variant="outline" isDisabled>
                    Load Template
                  </Button>
                </VStack>
              </Box>
            </VStack>
          </Box>

          {/* Main Workspace */}
          <Box flex={1} position="relative" overflow="hidden">
            {panels.length === 0 ? (
              <VStack 
                justify="center" 
                align="center" 
                h="100%" 
                spacing={4} 
                color="gray.500"
              >
                <Text fontSize="6xl">🏗️</Text>
                <Heading size="md" color="gray.600">
                  Welcome to Your Workspace
                </Heading>
                <Text textAlign="center" maxW="md">
                  Start building your custom dashboard by clicking on widgets from the sidebar. 
                  Drag, resize, and arrange panels to create your perfect blockchain intelligence workspace.
                </Text>
                <Button 
                  colorScheme="blue" 
                  onClick={() => addPanel('graph-explorer')}
                  size="lg"
                >
                  Add Your First Widget
                </Button>
              </VStack>
            ) : (
              <DockableLayout
                panels={panels}
                onPanelUpdate={(panelId, updates) => {
                  setPanels(panels.map(p => p.id === panelId ? { ...p, ...updates } : p));
                }}
                onPanelClose={(panelId) => {
                  setPanels(panels.filter(p => p.id !== panelId));
                }}
              />
            )}
          </Box>
        </HStack>
      </Box>
    </ThemeProvider>
  );
};

export default WorkspacePage;
