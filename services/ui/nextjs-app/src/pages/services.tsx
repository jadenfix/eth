import React from 'react';
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
  CardHeader,
  Badge,
  Icon,
  Button,
  Divider,
  useColorModeValue,
} from '@chakra-ui/react';
import { ThemeProvider } from '../components';
import Link from 'next/link';

interface ServiceCard {
  id: string;
  title: string;
  description: string;
  status: 'active' | 'beta' | 'coming-soon';
  category: 'ingestion' | 'intelligence' | 'visualization' | 'api' | 'security' | 'workflow';
  route?: string;
  icon: string;
  features: string[];
}

const services: ServiceCard[] = [
  // Ingestion Layer
  {
    id: 'ethereum-ingester',
    title: 'Ethereum Ingestion',
    description: 'Real-time blockchain data ingestion via Alchemy/Infura with TheGraph integration',
    status: 'active',
    category: 'ingestion',
    route: '/ingestion',
    icon: '⛓️',
    features: ['Real-time block data', 'Transaction monitoring', 'Event extraction', 'Multi-chain support']
  },
  
  // Semantic Fusion Layer
  {
    id: 'ontology',
    title: 'Ontology Service',
    description: 'GraphQL-powered metadata and relationship management with Neo4j backend',
    status: 'active',
    category: 'intelligence',
    route: '/ontology',
    icon: '🕸️',
    features: ['GraphQL API', 'Neo4j integration', 'Relationship mapping', 'Semantic queries']
  },
  {
    id: 'entity-resolution',
    title: 'Entity Resolution',
    description: 'AI-powered entity matching and resolution pipeline using Vertex AI',
    status: 'active',
    category: 'intelligence',
    route: '/intelligence/entities',
    icon: '🔍',
    features: ['AI matching', 'Entity clustering', 'Address resolution', 'Risk scoring']
  },
  
  // Intelligence & Agent Mesh
  {
    id: 'mev-agent',
    title: 'MEV Watch Agent',
    description: 'Real-time MEV opportunity detection and monitoring',
    status: 'active',
    category: 'intelligence',
    route: '/agents/mev',
    icon: '🤖',
    features: ['MEV detection', 'Arbitrage alerts', 'Sandwich monitoring', 'Liquidation tracking']
  },
  {
    id: 'risk-ai',
    title: 'Risk Intelligence',
    description: 'ML-powered fraud detection, anomaly analysis, and risk assessment',
    status: 'beta',
    category: 'intelligence',
    route: '/intelligence/risk',
    icon: '⚠️',
    features: ['Fraud detection', 'Anomaly analysis', 'Risk scoring', 'Pattern recognition']
  },
  {
    id: 'analytics',
    title: 'Analytics Dashboard',
    description: 'Real-time blockchain analytics with comprehensive metrics and insights',
    status: 'active',
    category: 'intelligence',
    route: '/analytics',
    icon: '📊',
    features: ['Real-time metrics', 'Interactive charts', 'Protocol analysis', 'Risk distribution']
  },
  
  // Visualization Layer
  {
    id: 'graph-explorer',
    title: 'Graph Explorer',
    description: 'Interactive network visualization with force-directed layouts',
    status: 'active',
    category: 'visualization',
    route: '/explorer',
    icon: '🌐',
    features: ['Force-directed graphs', 'Interactive exploration', 'Real-time updates', 'Custom layouts']
  },
  {
    id: 'timeseries-canvas',
    title: 'Time Series Canvas',
    description: 'High-performance time series charting and analytics',
    status: 'active',
    category: 'visualization',
    route: '/canvas',
    icon: '📊',
    features: ['Real-time charts', 'Multiple data sources', 'Interactive analysis', 'Export capabilities']
  },
  {
    id: 'compliance-map',
    title: 'Compliance Mapping',
    description: 'Choropleth maps and Sankey diagrams for regulatory compliance',
    status: 'active',
    category: 'visualization',
    route: '/compliance',
    icon: '🗺️',
    features: ['Regulatory mapping', 'Fund flow analysis', 'Compliance tracking', 'Risk visualization']
  },
  {
    id: 'workspace',
    title: 'Foundry Workspace',
    description: 'Drag-and-drop dashboard builder with customizable panels',
    status: 'beta',
    category: 'visualization',
    route: '/workspace',
    icon: '🏗️',
    features: ['Drag-and-drop', 'Custom dashboards', 'Panel layouts', 'Real-time data']
  },
  
  // API & Security Layer
  {
    id: 'api-gateway',
    title: 'API Gateway',
    description: 'Unified API access with authentication and rate limiting',
    status: 'active',
    category: 'api',
    route: '/api/docs',
    icon: '🚪',
    features: ['REST & GraphQL', 'Authentication', 'Rate limiting', 'API documentation']
  },
  {
    id: 'access-control',
    title: 'Access Control',
    description: 'Fine-grained access control with audit logging and DLP',
    status: 'active',
    category: 'security',
    route: '/security/access',
    icon: '🔐',
    features: ['Role-based access', 'Audit logging', 'Data masking', 'Compliance tracking']
  },
  
  // Workflow & VoiceOps
  {
    id: 'workflow-builder',
    title: 'Workflow Builder',
    description: 'Visual workflow and signal composition using Dagster',
    status: 'beta',
    category: 'workflow',
    route: '/workflows',
    icon: '⚙️',
    features: ['Visual builder', 'Signal composition', 'Automated workflows', 'Custom triggers']
  },
  {
    id: 'voiceops',
    title: 'VoiceOps',
    description: 'Voice-powered operations with ElevenLabs TTS/STT integration',
    status: 'beta',
    category: 'api',
    route: '/voice',
    icon: '🎤',
    features: ['Voice commands', 'Audio alerts', 'Speech recognition', 'Natural language']
  },
  
  // Monitoring & Health
  {
    id: 'monitoring',
    title: 'System Monitoring',
    description: 'Health monitoring and observability across all services',
    status: 'active',
    category: 'security',
    route: '/monitoring',
    icon: '📡',
    features: ['Health checks', 'Performance metrics', 'Alert management', 'System status']
  },
];

const categoryColors = {
  ingestion: 'blue',
  intelligence: 'purple',
  visualization: 'green',
  api: 'orange',
  security: 'red',
  workflow: 'teal',
};

const categoryIcons = {
  ingestion: '📥',
  intelligence: '🧠',
  visualization: '📈',
  api: '🔗',
  security: '🛡️',
  workflow: '🔄',
};

const ServicesPage: NextPage = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  const servicesByCategory = services.reduce((acc, service) => {
    if (!acc[service.category]) {
      acc[service.category] = [];
    }
    acc[service.category].push(service);
    return acc;
  }, {} as Record<string, ServiceCard[]>);

  return (
    <ThemeProvider>
      <Box bg={bgColor} minH="100vh">
        <Head>
          <title>Services Overview | Onchain Command Center</title>
          <meta name="description" content="Comprehensive overview of all available services in the Onchain Command Center platform" />
        </Head>

        <Container maxW="7xl" py={8}>
          <VStack spacing={8} align="stretch">
            {/* Header */}
            <Box textAlign="center" py={8}>
              <Heading size="2xl" mb={4}>
                Platform Services
              </Heading>
              <Text fontSize="xl" color="gray.600" maxW="3xl" mx="auto">
                Explore our comprehensive suite of blockchain intelligence and analytics services. 
                From real-time data ingestion to AI-powered insights and interactive visualizations.
              </Text>
            </Box>

            {/* Service Categories */}
            {Object.entries(servicesByCategory).map(([category, categoryServices]) => (
              <Box key={category}>
                <HStack mb={6} align="center">
                  <Text fontSize="3xl">{categoryIcons[category as keyof typeof categoryIcons]}</Text>
                  <Heading size="lg" textTransform="capitalize">
                    {category.replace('-', ' ')} Layer
                  </Heading>
                  <Badge colorScheme={categoryColors[category as keyof typeof categoryColors]} size="lg">
                    {categoryServices.length} services
                  </Badge>
                </HStack>

                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} mb={8}>
                  {categoryServices.map((service) => (
                    <Card key={service.id} bg={cardBg} shadow="md" _hover={{ shadow: 'lg', transform: 'translateY(-2px)' }} transition="all 0.2s">
                      <CardHeader pb={3}>
                        <HStack justify="space-between" align="start">
                          <HStack>
                            <Text fontSize="2xl">{service.icon}</Text>
                            <VStack align="start" spacing={1}>
                              <Heading size="md">{service.title}</Heading>
                              <Badge 
                                colorScheme={service.status === 'active' ? 'green' : service.status === 'beta' ? 'yellow' : 'gray'}
                                size="sm"
                              >
                                {service.status.replace('-', ' ')}
                              </Badge>
                            </VStack>
                          </HStack>
                        </HStack>
                      </CardHeader>

                      <CardBody pt={0}>
                        <Text fontSize="sm" color="gray.600" mb={4} noOfLines={3}>
                          {service.description}
                        </Text>

                        <VStack align="stretch" spacing={3}>
                          <Box>
                            <Text fontSize="xs" fontWeight="semibold" color="gray.500" mb={2}>
                              KEY FEATURES
                            </Text>
                            <VStack align="stretch" spacing={1}>
                              {service.features.slice(0, 3).map((feature, idx) => (
                                <HStack key={idx} fontSize="xs">
                                  <Text color="green.500">✓</Text>
                                  <Text>{feature}</Text>
                                </HStack>
                              ))}
                              {service.features.length > 3 && (
                                <Text fontSize="xs" color="gray.500">
                                  +{service.features.length - 3} more features
                                </Text>
                              )}
                            </VStack>
                          </Box>

                          <Divider />

                          <HStack justify="space-between">
                            {service.route && service.status === 'active' ? (
                              <Link href={service.route}>
                                <Button size="sm" colorScheme="blue" variant="solid">
                                  Access Service
                                </Button>
                              </Link>
                            ) : service.status === 'beta' ? (
                              <Button size="sm" colorScheme="yellow" variant="outline" isDisabled>
                                Beta Access
                              </Button>
                            ) : (
                              <Button size="sm" variant="ghost" isDisabled>
                                Coming Soon
                              </Button>
                            )}
                            
                            <Badge colorScheme={categoryColors[service.category as keyof typeof categoryColors]} variant="subtle">
                              {service.category}
                            </Badge>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </SimpleGrid>
                
                <Divider />
              </Box>
            ))}

            {/* Quick Stats */}
            <Box bg={cardBg} p={6} rounded="lg" shadow="md">
              <Heading size="md" mb={4}>Platform Overview</Heading>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                <VStack>
                  <Text fontSize="2xl" fontWeight="bold" color="blue.500">{services.length}</Text>
                  <Text fontSize="sm" color="gray.600">Total Services</Text>
                </VStack>
                <VStack>
                  <Text fontSize="2xl" fontWeight="bold" color="green.500">
                    {services.filter(s => s.status === 'active').length}
                  </Text>
                  <Text fontSize="sm" color="gray.600">Active Services</Text>
                </VStack>
                <VStack>
                  <Text fontSize="2xl" fontWeight="bold" color="yellow.500">
                    {services.filter(s => s.status === 'beta').length}
                  </Text>
                  <Text fontSize="sm" color="gray.600">Beta Services</Text>
                </VStack>
                <VStack>
                  <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                    {Object.keys(servicesByCategory).length}
                  </Text>
                  <Text fontSize="sm" color="gray.600">Service Categories</Text>
                </VStack>
              </SimpleGrid>
            </Box>
          </VStack>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default ServicesPage;
