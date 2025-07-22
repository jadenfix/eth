import React, { useState, useEffect } from 'react';
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
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Tab,
  Tabs,
  TabList,
  TabPanels,
  TabPanel,
} from '@chakra-ui/react';

interface EntityStats {
  totalEntities: number;
  addresses: number;
  contracts: number;
  tokens: number;
  labels: number;
  relationships: number;
  confidence: number;
  lastUpdate: string;
}

interface RecentEntity {
  id: string;
  type: 'address' | 'contract' | 'token' | 'exchange';
  address: string;
  label?: string;
  confidence: number;
  tags: string[];
  lastSeen: string;
}

const OntologyPage: NextPage = () => {
  const [stats, setStats] = useState<EntityStats>({
    totalEntities: 2456789,
    addresses: 1823456,
    contracts: 234567,
    tokens: 156789,
    labels: 89234,
    relationships: 4567890,
    confidence: 94.2,
    lastUpdate: new Date().toISOString(),
  });

  const [recentEntities, setRecentEntities] = useState<RecentEntity[]>([
    {
      id: 'ent1',
      type: 'exchange',
      address: '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD',
      label: 'Uniswap V3: Universal Router',
      confidence: 98.5,
      tags: ['DEX', 'AMM', 'Verified'],
      lastSeen: '2 minutes ago',
    },
    {
      id: 'ent2',
      type: 'contract',
      address: '0xA0b86a33E6411Bd3a4f37ad8A96cC5C9b4B2C5E1',
      label: 'USDC Token Contract',
      confidence: 99.8,
      tags: ['Stablecoin', 'ERC20', 'Circle'],
      lastSeen: '5 minutes ago',
    },
    {
      id: 'ent3',
      type: 'address',
      address: '0x742d35Cc8d3C8A9F99D4F7b79Da3E87C1b4b7F8d',
      confidence: 76.3,
      tags: ['High Volume', 'Whale'],
      lastSeen: '12 minutes ago',
    },
  ]);

  const bgColor = useColorModeValue('gray.100', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        totalEntities: prev.totalEntities + Math.floor(Math.random() * 10),
        confidence: 94.2 + (Math.random() - 0.5) * 2,
        lastUpdate: new Date().toISOString(),
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Box bg={bgColor} minH="100vh">
      <Head>
        <title>Ontology Service | Blockchain Intelligence</title>
        <meta name="description" content="Entity resolution and blockchain ontology management" />
      </Head>

      {/* Header */}
      <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={4} shadow="sm">
        <Container maxW="7xl" px={6}>
          <HStack justify="space-between" align="center">
            <HStack spacing={4}>
              <Link href="/services">
                <Button variant="ghost" size="sm">← All Services</Button>
              </Link>
              <Text fontSize="2xl">🧠</Text>
              <VStack align="start" spacing={0}>
                <Heading size="lg">Ontology Service</Heading>
                <Text color="gray.600">Entity Resolution & Knowledge Graph</Text>
              </VStack>
            </HStack>

            <HStack spacing={3}>
              <Badge 
                colorScheme={stats.confidence > 90 ? 'green' : 'yellow'} 
                variant="solid" 
                px={3} 
                py={1}
              >
                {stats.confidence.toFixed(1)}% CONFIDENCE
              </Badge>
              <Link href="/workspace">
                <Button colorScheme="blue">Open in Workspace</Button>
              </Link>
            </HStack>
          </HStack>
        </Container>
      </Box>

      <Container maxW="7xl" py={8} px={6}>
        <VStack spacing={8} align="stretch">
          
          {/* Stats Grid */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Total Entities</StatLabel>
                  <StatNumber fontSize="2xl">{stats.totalEntities.toLocaleString()}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +12.3% this hour
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Labeled Entities</StatLabel>
                  <StatNumber fontSize="2xl">{stats.labels.toLocaleString()}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +8.7% this hour
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Relationships</StatLabel>
                  <StatNumber fontSize="2xl">{(stats.relationships / 1000000).toFixed(1)}M</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +15.2% this hour
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Avg Confidence</StatLabel>
                  <StatNumber fontSize="2xl">{stats.confidence.toFixed(1)}%</StatNumber>
                  <StatHelpText>Model accuracy</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Tabs Section */}
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">Entity Management</Heading>
            </CardHeader>
            <CardBody>
              <Tabs variant="enclosed">
                <TabList>
                  <Tab>Recent Entities</Tab>
                  <Tab>Entity Types</Tab>
                  <Tab>Resolution Pipeline</Tab>
                  <Tab>Knowledge Graph</Tab>
                </TabList>

                <TabPanels>
                  {/* Recent Entities Tab */}
                  <TabPanel px={0}>
                    <TableContainer>
                      <Table size="sm">
                        <Thead>
                          <Tr>
                            <Th>Address</Th>
                            <Th>Type</Th>
                            <Th>Label</Th>
                            <Th>Confidence</Th>
                            <Th>Tags</Th>
                            <Th>Last Seen</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {recentEntities.map((entity) => (
                            <Tr key={entity.id}>
                              <Td>
                                <Text 
                                  fontFamily="mono" 
                                  fontSize="xs"
                                  color="blue.600"
                                  cursor="pointer"
                                  _hover={{ textDecor: 'underline' }}
                                >
                                  {entity.address.slice(0, 10)}...{entity.address.slice(-8)}
                                </Text>
                              </Td>
                              <Td>
                                <Badge 
                                  colorScheme={
                                    entity.type === 'exchange' ? 'purple' :
                                    entity.type === 'contract' ? 'blue' :
                                    entity.type === 'token' ? 'green' : 'gray'
                                  }
                                  variant="subtle"
                                >
                                  {entity.type}
                                </Badge>
                              </Td>
                              <Td>
                                <Text fontSize="sm" fontWeight="medium">
                                  {entity.label || 'Unlabeled'}
                                </Text>
                              </Td>
                              <Td>
                                <VStack align="start" spacing={1}>
                                  <Text fontSize="sm">{entity.confidence.toFixed(1)}%</Text>
                                  <Progress 
                                    value={entity.confidence} 
                                    size="xs" 
                                    width="60px"
                                    colorScheme={entity.confidence > 90 ? 'green' : entity.confidence > 70 ? 'yellow' : 'red'}
                                  />
                                </VStack>
                              </Td>
                              <Td>
                                <HStack spacing={1} wrap="wrap">
                                  {entity.tags.map((tag, idx) => (
                                    <Badge key={idx} size="xs" variant="outline">
                                      {tag}
                                    </Badge>
                                  ))}
                                </HStack>
                              </Td>
                              <Td>
                                <Text fontSize="xs" color="gray.500">
                                  {entity.lastSeen}
                                </Text>
                              </Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </TabPanel>

                  {/* Entity Types Tab */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                      <Card size="sm">
                        <CardHeader pb={2}>
                          <Text fontWeight="medium">Addresses</Text>
                        </CardHeader>
                        <CardBody pt={0}>
                          <VStack align="stretch" spacing={2}>
                            <HStack justify="space-between">
                              <Text fontSize="sm">EOAs</Text>
                              <Text fontSize="sm" fontWeight="medium">1.2M</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Contract Addresses</Text>
                              <Text fontSize="sm" fontWeight="medium">234K</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Multi-sig</Text>
                              <Text fontSize="sm" fontWeight="medium">45K</Text>
                            </HStack>
                          </VStack>
                        </CardBody>
                      </Card>

                      <Card size="sm">
                        <CardHeader pb={2}>
                          <Text fontWeight="medium">Contracts</Text>
                        </CardHeader>
                        <CardBody pt={0}>
                          <VStack align="stretch" spacing={2}>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Token Contracts</Text>
                              <Text fontSize="sm" fontWeight="medium">156K</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">DEX Contracts</Text>
                              <Text fontSize="sm" fontWeight="medium">12K</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">DeFi Protocols</Text>
                              <Text fontSize="sm" fontWeight="medium">8.9K</Text>
                            </HStack>
                          </VStack>
                        </CardBody>
                      </Card>
                    </SimpleGrid>
                  </TabPanel>

                  {/* Resolution Pipeline Tab */}
                  <TabPanel px={0}>
                    <VStack spacing={4} align="stretch">
                      <Text color="gray.600">
                        Real-time entity resolution pipeline processes incoming blockchain data 
                        and maps entities to known labels and relationships.
                      </Text>
                      
                      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                        <Box p={4} border="1px solid" borderColor="gray.200" borderRadius="md">
                          <VStack spacing={2}>
                            <Text fontSize="2xl">📥</Text>
                            <Text fontWeight="medium">Data Ingestion</Text>
                            <Text fontSize="sm" color="gray.600" textAlign="center">
                              Raw blockchain data collection and preprocessing
                            </Text>
                          </VStack>
                        </Box>

                        <Box p={4} border="1px solid" borderColor="gray.200" borderRadius="md">
                          <VStack spacing={2}>
                            <Text fontSize="2xl">🔍</Text>
                            <Text fontWeight="medium">Entity Resolution</Text>
                            <Text fontSize="sm" color="gray.600" textAlign="center">
                              ML-powered entity identification and labeling
                            </Text>
                          </VStack>
                        </Box>

                        <Box p={4} border="1px solid" borderColor="gray.200" borderRadius="md">
                          <VStack spacing={2}>
                            <Text fontSize="2xl">🧠</Text>
                            <Text fontWeight="medium">Knowledge Graph</Text>
                            <Text fontSize="sm" color="gray.600" textAlign="center">
                              Relationship mapping and graph construction
                            </Text>
                          </VStack>
                        </Box>
                      </SimpleGrid>
                    </VStack>
                  </TabPanel>

                  {/* Knowledge Graph Tab */}
                  <TabPanel px={0}>
                    <VStack spacing={4} align="stretch">
                      <Text color="gray.600">
                        Interactive knowledge graph visualization showing entity relationships 
                        and network topology.
                      </Text>
                      
                      <Box 
                        height="300px" 
                        bg="gray.50" 
                        border="1px dashed" 
                        borderColor="gray.300"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        borderRadius="md"
                      >
                        <VStack spacing={3}>
                          <Text fontSize="4xl">🕸️</Text>
                          <Text fontWeight="medium" color="gray.600">
                            Knowledge Graph Visualization
                          </Text>
                          <Text fontSize="sm" color="gray.500" textAlign="center">
                            Interactive network graph showing entity relationships<br/>
                            and semantic connections
                          </Text>
                          <Button size="sm" colorScheme="blue" variant="outline">
                            Launch Graph Explorer
                          </Button>
                        </VStack>
                      </Box>
                    </VStack>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </CardBody>
          </Card>

          {/* Quick Actions */}
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">Quick Actions</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={3}>
                <Button size="sm" variant="outline" leftIcon={<Text>🔍</Text>}>
                  Search Entities
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>➕</Text>}>
                  Add Label
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>📊</Text>}>
                  View Analytics
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>⚙️</Text>}>
                  Configure ML
                </Button>
              </SimpleGrid>
            </CardBody>
          </Card>

        </VStack>
      </Container>
    </Box>
  );
};

export default OntologyPage;
