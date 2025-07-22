import React from 'react';
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
  CardHeader,
  Badge,
  Divider,
  List,
  ListItem,
  ListIcon,
  Stack,
} from '@chakra-ui/react';
import { ChevronRightIcon } from '@chakra-ui/icons';
import { ResponsiveLayout } from '../src/components';

interface ArchitectureLayer {
  id: string;
  number: number;
  name: string;
  description: string;
  icon: string;
  color: string;
  services: string[];
  technologies: string[];
  keyFeatures: string[];
}

const ArchitecturePage: NextPage = () => {
  const layers: ArchitectureLayer[] = [
    {
      id: 'identity',
      number: 0,
      name: 'Identity & Access',
      description: 'Cloud IAM with BigQuery column-level ACLs and Cloud DLP redaction',
      icon: '🔐',
      color: 'red',
      services: ['Access Control', 'Audit Logging', 'Cloud DLP'],
      technologies: ['Cloud IAM', 'BigQuery ACLs', 'Cloud DLP', 'SOC-2'],
      keyFeatures: ['Role-based access', 'Column-level security', 'Audit trails', 'Data masking']
    },
    {
      id: 'ingestion',
      number: 1,
      name: 'Ingestion Layer',
      description: 'Cloud Functions → Pub/Sub → Dataflow pipeline for real-time blockchain data',
      icon: '📥',
      color: 'orange',
      services: ['Ethereum Ingestion', 'Data Pipeline'],
      technologies: ['Cloud Functions', 'Pub/Sub', 'Dataflow', 'BigQuery', 'TheGraph'],
      keyFeatures: ['Real-time ingestion', 'Multi-chain support', 'Event normalization', 'Scalable pipeline']
    },
    {
      id: 'semantic',
      number: 2,
      name: 'Semantic Fusion Layer',
      description: 'Ontology service with GraphQL and AI-powered entity resolution',
      icon: '🧠',
      color: 'yellow',
      services: ['Ontology Service', 'Graph API', 'Entity Resolution'],
      technologies: ['GraphQL', 'Neo4j Aura', 'Vertex AI', 'Dataplex'],
      keyFeatures: ['Knowledge graph', 'Entity matching', 'Relationship mapping', 'Semantic queries']
    },
    {
      id: 'intelligence',
      number: 3,
      name: 'Intelligence & Agent Mesh',
      description: 'Vertex AI pipelines with GKE agent mesh for MEV, fraud, and risk detection',
      icon: '🤖',
      color: 'green',
      services: ['MEV Watch Agent', 'Analytics Dashboard', 'Risk Intelligence'],
      technologies: ['Vertex AI', 'GKE', 'GBDT', 'Graph-SAGE', 'Auto-encoders'],
      keyFeatures: ['Anomaly detection', 'MEV monitoring', 'Fraud detection', 'Risk scoring']
    },
    {
      id: 'api',
      number: 4,
      name: 'API & VoiceOps Layer',
      description: 'gRPC + REST APIs with WebSocket streaming and ElevenLabs voice integration',
      icon: '🚪',
      color: 'blue',
      services: ['API Gateway', 'VoiceOps Service'],
      technologies: ['gRPC', 'REST', 'WebSocket', 'Cloud Run', 'ElevenLabs'],
      keyFeatures: ['Unified API', 'Real-time streaming', 'Voice commands', 'TTS/STT']
    },
    {
      id: 'visualization',
      number: 5,
      name: 'Visualization Layer',
      description: 'Palantir Foundry-style interactive dashboards and analytical interfaces',
      icon: '📊',
      color: 'purple',
      services: ['DeckGL Explorer', 'Time Series Canvas', 'Compliance Map', 'Foundry Workspace'],
      technologies: ['Deck.GL', 'WebGL', 'Plotly.js', 'D3', 'React DnD'],
      keyFeatures: ['Interactive graphs', 'Real-time charts', 'Drag-drop dashboards', 'WebGL rendering']
    },
    {
      id: 'ux',
      number: 6,
      name: 'UX & Workflow Builder',
      description: 'Next.js war room with Dagster workflow builder and multi-platform integration',
      icon: '🏗️',
      color: 'pink',
      services: ['Status Dashboard', 'Workflow Builder', 'Health Monitoring'],
      technologies: ['Next.js', 'ChakraUI', 'Dagster', 'Slack', 'MS Teams'],
      keyFeatures: ['Visual workflows', 'Real-time dashboards', 'Multi-platform', 'Low-code builder']
    }
  ];

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  return (
    <ResponsiveLayout 
      title="System Architecture | Blockchain Intelligence Platform"
      description="7-layer Palantir-grade blockchain intelligence architecture"
    >
      <Head>
        <title>System Architecture | Blockchain Intelligence Platform</title>
        <meta name="description" content="7-layer Palantir-grade blockchain intelligence architecture" />
      </Head>

      <Box bg={bgColor} minH="100vh">

      {/* Header */}
      <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={6} shadow="sm">
        <Container maxW="7xl" px={6}>
          <VStack spacing={4} align="center">
            <HStack spacing={4}>
              <Link href="/">
                <Button variant="ghost" size="sm">← Dashboard</Button>
              </Link>
              <Text fontSize="3xl">🏛️</Text>
              <VStack align="center" spacing={1}>
                <Heading size="xl">System Architecture</Heading>
                <Text color="gray.600" textAlign="center">
                  7-Layer Palantir-Grade Blockchain Intelligence Platform
                </Text>
              </VStack>
            </HStack>
            
            <HStack spacing={4}>
              <Badge colorScheme="blue" variant="solid" px={3} py={1} fontSize="sm">
                PRODUCTION READY
              </Badge>
              <Badge colorScheme="green" variant="solid" px={3} py={1} fontSize="sm">
                SOC-2 COMPLIANT
              </Badge>
              <Badge colorScheme="purple" variant="solid" px={3} py={1} fontSize="sm">
                FOUNDRY-STYLE
              </Badge>
            </HStack>
          </VStack>
        </Container>
      </Box>

      <Container maxW="7xl" py={10} px={6}>
        <VStack spacing={8} align="stretch">
          
          {/* Architecture Overview */}
          <Card bg={cardBg} size="lg">
            <CardHeader>
              <VStack spacing={3} align="center">
                <Heading size="lg">Onchain Command Center Architecture</Heading>
                <Text color="gray.600" textAlign="center" maxW="4xl">
                  Built with enterprise-grade scalability, security, and compliance in mind. 
                  Each layer provides distinct capabilities while seamlessly integrating with others.
                </Text>
              </VStack>
            </CardHeader>
          </Card>

          {/* Architecture Layers */}
          <VStack spacing={6}>
            {layers.map((layer, index) => (
              <Card key={layer.id} bg={cardBg} size="lg" width="100%">
                <CardBody p={8}>
                  <HStack spacing={6} align="start">
                    
                    {/* Layer Number & Icon */}
                    <VStack spacing={2} minW="80px">
                      <Box
                        bg={`${layer.color}.100`}
                        color={`${layer.color}.600`}
                        borderRadius="full"
                        p={4}
                        fontSize="2xl"
                      >
                        {layer.icon}
                      </Box>
                      <Badge colorScheme={layer.color} variant="solid" fontSize="sm">
                        LAYER {layer.number}
                      </Badge>
                    </VStack>

                    {/* Layer Details */}
                    <VStack align="start" flex={1} spacing={4}>
                      <VStack align="start" spacing={2}>
                        <Heading size="lg" color={`${layer.color}.600`}>
                          {layer.name}
                        </Heading>
                        <Text color="gray.600" fontSize="lg">
                          {layer.description}
                        </Text>
                      </VStack>

                      <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6} width="100%">
                        
                        {/* Services */}
                        <VStack align="start" spacing={3}>
                          <Text fontWeight="bold" color="gray.700">Services</Text>
                          <List spacing={2}>
                            {layer.services.map((service, idx) => (
                              <ListItem key={idx}>
                                <HStack spacing={2}>
                                  <ListIcon as={ChevronRightIcon} color={`${layer.color}.500`} />
                                  <Text fontSize="sm">{service}</Text>
                                </HStack>
                              </ListItem>
                            ))}
                          </List>
                        </VStack>

                        {/* Technologies */}
                        <VStack align="start" spacing={3}>
                          <Text fontWeight="bold" color="gray.700">Technologies</Text>
                          <Stack direction="row" wrap="wrap" spacing={2}>
                            {layer.technologies.map((tech, idx) => (
                              <Badge 
                                key={idx} 
                                colorScheme={layer.color} 
                                variant="outline" 
                                size="sm"
                              >
                                {tech}
                              </Badge>
                            ))}
                          </Stack>
                        </VStack>

                        {/* Key Features */}
                        <VStack align="start" spacing={3}>
                          <Text fontWeight="bold" color="gray.700">Key Features</Text>
                          <List spacing={2}>
                            {layer.keyFeatures.map((feature, idx) => (
                              <ListItem key={idx}>
                                <HStack spacing={2}>
                                  <ListIcon as={ChevronRightIcon} color={`${layer.color}.500`} />
                                  <Text fontSize="sm">{feature}</Text>
                                </HStack>
                              </ListItem>
                            ))}
                          </List>
                        </VStack>

                      </SimpleGrid>
                    </VStack>

                  </HStack>
                </CardBody>
                
                {index < layers.length - 1 && (
                  <Box textAlign="center" py={2}>
                    <Text fontSize="2xl" color="gray.400">↓</Text>
                  </Box>
                )}
              </Card>
            ))}
          </VStack>

          {/* Data Flow */}
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="lg" textAlign="center">Data Flow Architecture</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4}>
                <Text color="gray.600" textAlign="center">
                  Information flows seamlessly through each layer, from raw blockchain data to actionable intelligence
                </Text>
                
                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} width="100%">
                  
                  <Card variant="outline">
                    <CardBody textAlign="center">
                      <VStack spacing={3}>
                        <Text fontSize="2xl">📊</Text>
                        <Text fontWeight="bold">Data Ingestion</Text>
                        <Text fontSize="sm" color="gray.600">
                          Raw blockchain events → Normalized JSON → BigQuery storage
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card variant="outline">
                    <CardBody textAlign="center">
                      <VStack spacing={3}>
                        <Text fontSize="2xl">🧠</Text>
                        <Text fontWeight="bold">Intelligence Processing</Text>
                        <Text fontSize="sm" color="gray.600">
                          Entity resolution → AI analysis → Signal generation
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card variant="outline">
                    <CardBody textAlign="center">
                      <VStack spacing={3}>
                        <Text fontSize="2xl">💡</Text>
                        <Text fontWeight="bold">User Experience</Text>
                        <Text fontSize="sm" color="gray.600">
                          Interactive dashboards → Analyst workflows → Actions
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>

                </SimpleGrid>
              </VStack>
            </CardBody>
          </Card>

          {/* Quick Navigation */}
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">Explore the Platform</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                <Link href="/services">
                  <Button size="lg" variant="outline" leftIcon={<Text>🏢</Text>} width="100%">
                    All Services
                  </Button>
                </Link>
                <Link href="/workspace">
                  <Button size="lg" variant="outline" leftIcon={<Text>🏗️</Text>} width="100%">
                    Workspace
                  </Button>
                </Link>
                <Link href="/analytics">
                  <Button size="lg" variant="outline" leftIcon={<Text>📊</Text>} width="100%">
                    Analytics
                  </Button>
                </Link>
                <Link href="/status">
                  <Button size="lg" variant="outline" leftIcon={<Text>📋</Text>} width="100%">
                    System Status
                  </Button>
                </Link>
              </SimpleGrid>
            </CardBody>
          </Card>

        </VStack>
      </Container>
    </Box>
    </ResponsiveLayout>
  );
};

export default ArchitecturePage;
