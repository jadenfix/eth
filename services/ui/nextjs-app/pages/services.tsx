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
import CleanNavigation from '../src/components/layout/CleanNavigation';
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
  // Layer 1: Ingestion Layer
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
  {
    id: 'ingestion-pipeline',
    title: 'Data Ingestion Pipeline', 
    description: 'Cloud Functions → Pub/Sub → Dataflow pipeline for blockchain data processing',
    status: 'active',
    category: 'ingestion',
    route: '/ingestion/pipeline',
    icon: '🔄',
    features: ['Cloud Functions', 'Pub/Sub messaging', 'Dataflow processing', 'BigQuery storage']
  },
  
  // Layer 2: Semantic Fusion Layer
  {
    id: 'ontology',
    title: 'Ontology Service',
    description: 'GraphQL-powered metadata and relationship management with Neo4j backend',
    status: 'active',
    category: 'intelligence',
    route: '/ontology',
    icon: '🧠',
    features: ['GraphQL API', 'Neo4j integration', 'Relationship mapping', 'Semantic queries']
  },
  {
    id: 'graph-api',
    title: 'Graph API',
    description: 'High-performance graph query API for blockchain entity relationships',
    status: 'active',
    category: 'intelligence',
    route: '/graph/api',
    icon: '🕸️',
    features: ['Graph queries', 'Entity traversal', 'Relationship analysis', 'Performance optimized']
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
  
  // Layer 3: Intelligence & Agent Mesh
  {
    id: 'mev-agent',
    title: 'MEV Watch Agent',
    description: 'Real-time MEV opportunity detection and monitoring service',
    status: 'active',
    category: 'intelligence',
    route: '/mev',
    icon: '🤖',
    features: ['MEV detection', 'Arbitrage alerts', 'Sandwich monitoring', 'Liquidation tracking']
  },
  {
    id: 'whale-tracker',
    title: 'Whale Tracker',
    description: 'Large transaction monitoring and whale movement analysis',
    status: 'active',
    category: 'intelligence',
    route: '/intelligence/whales',
    icon: '🐋',
    features: ['Whale detection', 'Movement tracking', 'Impact analysis', 'Alert system']
  },
  {
    id: 'sanctions-alert',
    title: 'Sanctions Alert',
    description: 'OFAC compliance monitoring and sanctions screening service',
    status: 'active',
    category: 'security',
    route: '/security/sanctions',
    icon: '🚨',
    features: ['OFAC screening', 'Compliance alerts', 'Risk assessment', 'Audit trail']
  },
  
  // Layer 4: API & VoiceOps Layer
  {
    id: 'voice-ops',
    title: 'Voice Operations',
    description: 'ElevenLabs-powered voice commands and TTS alerts for hands-free operation',
    status: 'active',
    category: 'api',
    route: '/voice',
    icon: '🎤',
    features: ['Voice commands', 'TTS alerts', 'STT processing', 'Natural language']
  },
  {
    id: 'api-gateway',
    title: 'API Gateway',
    description: 'Unified REST and GraphQL API gateway with authentication and rate limiting',
    status: 'active',
    category: 'api',
    route: '/api/gateway',
    icon: '🌐',
    features: ['REST API', 'GraphQL', 'Authentication', 'Rate limiting']
  },
  
  // Layer 5: UX & Workflow Builder
  {
    id: 'workflow-builder',
    title: 'Workflow Builder',
    description: 'Dagster-powered visual workflow builder for custom signal creation',
    status: 'beta',
    category: 'workflow',
    route: '/workflows/dagster',
    icon: '⚙️',
    features: ['Visual builder', 'Custom signals', 'Dagster integration', 'Low-code']
  },
  {
    id: 'signal-marketplace',
    title: 'Signal Marketplace',
    description: 'Community-driven marketplace for trading and sharing blockchain signals',
    status: 'coming-soon',
    category: 'workflow',
    route: '/marketplace',
    icon: '🏪',
    features: ['Signal trading', 'Community sharing', 'Revenue sharing', 'Quality control']
  },
  
  // Layer 6: Launch & Growth
  {
    id: 'billing-metering',
    title: 'Billing & Metering',
    description: 'Stripe-powered usage-based billing and metering system',
    status: 'active',
    category: 'api',
    route: '/billing',
    icon: '💳',
    features: ['Usage metering', 'Stripe integration', 'Usage analytics', 'Billing automation']
  },
  {
    id: 'token-gate',
    title: 'Token Gate',
    description: 'Pond Markets integration for token-gated access control',
    status: 'coming-soon',
    category: 'security',
    route: '/security/token-gate',
    icon: '🔐',
    features: ['Token verification', 'Access control', 'Pond Markets', 'NFT gating']
  }
];

const categoryIcons = {
  ingestion: '📥',
  intelligence: '🧠',
  visualization: '📊',
  api: '🔌',
  security: '🔒',
  workflow: '⚙️'
};

const categoryColors = {
  ingestion: 'blue',
  intelligence: 'purple',
  visualization: 'cyan',
  api: 'green',
  security: 'red',
  workflow: 'orange'
};

const ServicesPage: NextPage = () => {
  // Enhanced color mode values with better contrast
  const bgColor = useColorModeValue('gray.50', 'palantir.navy');
  const cardBg = useColorModeValue('white', 'palantir.navy-light');
  const textColor = useColorModeValue('gray.900', 'white');
  const mutedTextColor = useColorModeValue('gray.700', 'gray.300');
  const subtleTextColor = useColorModeValue('gray.600', 'gray.400');
  const cardBorderColor = useColorModeValue('gray.200', 'gray.600');

  const servicesByCategory = services.reduce((acc, service) => {
    if (!acc[service.category]) {
      acc[service.category] = [];
    }
    acc[service.category].push(service);
    return acc;
  }, {} as Record<string, ServiceCard[]>);

  return (
    <Box bg={bg} minH="100vh">
      <CleanNavigation />
      
      <Box p={6}>
      <Head>
        <title>Services Overview | Onchain Command Center</title>
        <meta name="description" content="Comprehensive overview of all available services in the Onchain Command Center platform" />
      </Head>

      <Container maxW="7xl" px={{ base: 4, md: 6, lg: 8 }}>
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box textAlign="center" py={8}>
            <Heading size="2xl" mb={4} color={textColor} fontWeight="bold">
              Platform Services
            </Heading>
            <Text fontSize="xl" color={mutedTextColor} maxW="3xl" mx="auto" fontWeight="medium">
              Explore our comprehensive suite of blockchain intelligence and analytics services. 
              From real-time data ingestion to AI-powered insights and interactive visualizations.
            </Text>
          </Box>

          {/* Service Categories */}
          {Object.entries(servicesByCategory).map(([category, categoryServices]) => (
            <Box key={category}>
              <HStack mb={6} align="center">
                <Text fontSize="3xl">{categoryIcons[category as keyof typeof categoryIcons]}</Text>
                <Heading size="lg" textTransform="capitalize" color={textColor} fontWeight="bold">
                  {category.replace('-', ' ')} Layer
                </Heading>
                <Badge colorScheme={categoryColors[category as keyof typeof categoryColors]} size="lg" px={3} py={1}>
                  {categoryServices.length} services
                </Badge>
              </HStack>

              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} mb={8}>
                {categoryServices.map((service) => (
                  <Card 
                    key={service.id} 
                    bg={cardBg} 
                    border="1px solid" 
                    borderColor={cardBorderColor}
                    shadow="md" 
                    _hover={{ 
                      shadow: 'lg', 
                      transform: 'translateY(-2px)',
                      borderColor: useColorModeValue('gray.300', 'gray.500')
                    }} 
                    transition="all 0.2s"
                  >
                    <CardHeader pb={3}>
                      <HStack justify="space-between" align="start">
                        <HStack>
                          <Text fontSize="2xl">{service.icon}</Text>
                          <VStack align="start" spacing={1}>
                            <Heading size="md" color={textColor} fontWeight="bold">{service.title}</Heading>
                            <Badge 
                              colorScheme={service.status === 'active' ? 'success' : service.status === 'beta' ? 'warning' : 'gray'}
                              size="sm"
                              px={2}
                              py={1}
                            >
                              {service.status.replace('-', ' ')}
                            </Badge>
                          </VStack>
                        </HStack>
                      </HStack>
                    </CardHeader>

                    <CardBody pt={0}>
                      <Text fontSize="sm" color={mutedTextColor} mb={4} noOfLines={3} fontWeight="medium">
                        {service.description}
                      </Text>

                      <VStack align="stretch" spacing={3}>
                        <Box>
                          <Text fontSize="xs" fontWeight="semibold" color={subtleTextColor} mb={2} textTransform="uppercase">
                            Key Features
                          </Text>
                          <VStack align="stretch" spacing={1}>
                            {service.features.slice(0, 3).map((feature, idx) => (
                              <HStack key={idx} fontSize="xs">
                                <Text color="success.500" fontWeight="bold">✓</Text>
                                <Text color={mutedTextColor}>{feature}</Text>
                              </HStack>
                            ))}
                            {service.features.length > 3 && (
                              <Text fontSize="xs" color={subtleTextColor}>
                                +{service.features.length - 3} more features
                              </Text>
                            )}
                          </VStack>
                        </Box>

                        <Divider borderColor={useColorModeValue('gray.200', 'gray.600')} />

                        <HStack justify="space-between">
                          {service.route && service.status === 'active' ? (
                            <Link href={service.route}>
                              <Button size="sm" colorScheme="brand" variant="solid">
                                Access Service
                              </Button>
                            </Link>
                          ) : (
                            <Button size="sm" variant="outline" colorScheme="gray" isDisabled>
                              {service.status === 'beta' ? 'Coming Soon' : 'In Development'}
                            </Button>
                          )}
                          
                          <Badge 
                            colorScheme={categoryColors[category as keyof typeof categoryColors]} 
                            variant="subtle"
                            size="sm"
                          >
                            {category}
                          </Badge>
                        </HStack>
                      </VStack>
                    </CardBody>
                  </Card>
                ))}
              </SimpleGrid>
            </Box>
          ))}
        </VStack>
      </Container>
          </Box>
    </Box>
  );
};

export default ServicesPage;
