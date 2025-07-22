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
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Button,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Table,
  Tbody,
  Tr,
  Td,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { ThemeProvider } from '../components';

const IngestionPage: NextPage = () => {
  const [realTimeData, setRealTimeData] = useState({
    blocksProcessed: 18456789,
    transactionsPerSecond: 127,
    dataLatency: '2.3s',
    errorRate: 0.02,
  });

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  // Mock real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setRealTimeData(prev => ({
        ...prev,
        blocksProcessed: prev.blocksProcessed + Math.floor(Math.random() * 3),
        transactionsPerSecond: 120 + Math.floor(Math.random() * 20),
        dataLatency: (2 + Math.random()).toFixed(1) + 's',
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const dataSources = [
    { name: 'Alchemy Mainnet', status: 'active', tps: 142, latency: '1.8s' },
    { name: 'Infura Polygon', status: 'active', tps: 89, latency: '2.1s' },
    { name: 'TheGraph Protocol', status: 'active', tps: 67, latency: '3.2s' },
    { name: 'Arbitrum RPC', status: 'active', tps: 34, latency: '2.8s' },
    { name: 'Optimism Gateway', status: 'warning', tps: 12, latency: '5.1s' },
    { name: 'BSC Node', status: 'maintenance', tps: 0, latency: 'N/A' },
  ];

  const recentBlocks = [
    { number: 18456789, hash: '0x1a2b3c...', txCount: 247, timestamp: '12s ago', size: '84.2 KB' },
    { number: 18456788, hash: '0x4d5e6f...', txCount: 189, timestamp: '24s ago', size: '76.8 KB' },
    { number: 18456787, hash: '0x7g8h9i...', txCount: 312, timestamp: '36s ago', size: '91.5 KB' },
    { number: 18456786, hash: '0xj1k2l3...', txCount: 156, timestamp: '48s ago', size: '62.3 KB' },
  ];

  return (
    <ThemeProvider>
      <Box bg={bgColor} minH="100vh">
        <Head>
          <title>Data Ingestion | Onchain Command Center</title>
          <meta name="description" content="Real-time blockchain data ingestion and processing" />
        </Head>

        {/* Header */}
        <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={4} shadow="sm">
          <Container maxW="7xl">
            <HStack justify="space-between" align="center">
              <VStack align="start" spacing={1}>
                <HStack>
                  <Link href="/">
                    <Button variant="ghost" size="sm">← Back</Button>
                  </Link>
                  <Text fontSize="2xl">⛓️</Text>
                  <Heading size="lg">Data Ingestion Layer</Heading>
                </HStack>
                <Text color="gray.600">Real-time blockchain data processing and normalization</Text>
              </VStack>
              <HStack spacing={3}>
                <Badge colorScheme="green" variant="solid" px={3} py={1}>
                  ACTIVE
                </Badge>
                <Link href="/services">
                  <Button variant="outline" size="sm">All Services</Button>
                </Link>
              </HStack>
            </HStack>
          </Container>
        </Box>

        <Container maxW="7xl" py={8}>
          <VStack spacing={8} align="stretch">
            
            {/* Key Metrics */}
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
              <Card bg={cardBg} shadow="md">
                <CardBody>
                  <Stat>
                    <StatLabel>Blocks Processed</StatLabel>
                    <StatNumber>{realTimeData.blocksProcessed.toLocaleString()}</StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      Live updating
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
              
              <Card bg={cardBg} shadow="md">
                <CardBody>
                  <Stat>
                    <StatLabel>Transactions/Second</StatLabel>
                    <StatNumber>{realTimeData.transactionsPerSecond}</StatNumber>
                    <StatHelpText>
                      Current throughput
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
              
              <Card bg={cardBg} shadow="md">
                <CardBody>
                  <Stat>
                    <StatLabel>Data Latency</StatLabel>
                    <StatNumber>{realTimeData.dataLatency}</StatNumber>
                    <StatHelpText>
                      Average delay
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
              
              <Card bg={cardBg} shadow="md">
                <CardBody>
                  <Stat>
                    <StatLabel>Error Rate</StatLabel>
                    <StatNumber>{realTimeData.errorRate}%</StatNumber>
                    <StatHelpText>
                      <StatArrow type="decrease" />
                      Last 24h
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            </SimpleGrid>

            {/* Data Sources Status */}
            <Card bg={cardBg} shadow="md">
              <CardHeader>
                <Heading size="md">Data Sources</Heading>
                <Text fontSize="sm" color="gray.600">
                  Real-time status of blockchain data providers
                </Text>
              </CardHeader>
              <CardBody pt={0}>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {dataSources.map((source, idx) => (
                    <Card key={idx} variant="outline">
                      <CardBody p={4}>
                        <VStack spacing={3} align="stretch">
                          <HStack justify="space-between">
                            <Text fontWeight="semibold" fontSize="sm">{source.name}</Text>
                            <Badge 
                              colorScheme={
                                source.status === 'active' ? 'green' : 
                                source.status === 'warning' ? 'yellow' : 'red'
                              }
                              size="sm"
                            >
                              {source.status}
                            </Badge>
                          </HStack>
                          
                          <VStack spacing={2} align="stretch">
                            <HStack justify="space-between">
                              <Text fontSize="xs" color="gray.600">TPS:</Text>
                              <Text fontSize="xs">{source.tps}</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="xs" color="gray.600">Latency:</Text>
                              <Text fontSize="xs">{source.latency}</Text>
                            </HStack>
                          </VStack>
                          
                          <Progress 
                            value={source.status === 'active' ? 100 : source.status === 'warning' ? 60 : 0}
                            colorScheme={
                              source.status === 'active' ? 'green' : 
                              source.status === 'warning' ? 'yellow' : 'red'
                            }
                            size="sm"
                          />
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </SimpleGrid>
              </CardBody>
            </Card>

            {/* Live Data Feed */}
            <Card bg={cardBg} shadow="md">
              <CardHeader>
                <Heading size="md">Live Block Feed</Heading>
                <Text fontSize="sm" color="gray.600">
                  Recent blocks processed in real-time
                </Text>
              </CardHeader>
              <CardBody pt={0}>
                <Table variant="simple" size="sm">
                  <Tbody>
                    {recentBlocks.map((block, idx) => (
                      <Tr key={idx}>
                        <Td>
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="semibold" fontSize="sm">#{block.number}</Text>
                            <Text fontSize="xs" color="gray.500">{block.hash}</Text>
                          </VStack>
                        </Td>
                        <Td>
                          <Text fontSize="sm">{block.txCount} txs</Text>
                        </Td>
                        <Td>
                          <Text fontSize="sm">{block.size}</Text>
                        </Td>
                        <Td>
                          <Badge variant="subtle" colorScheme="blue">
                            {block.timestamp}
                          </Badge>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </CardBody>
            </Card>

            {/* System Health */}
            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
              <Card bg={cardBg} shadow="md">
                <CardHeader>
                  <Heading size="md">System Health</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={4}>
                    <Alert status="success" borderRadius="md">
                      <AlertIcon />
                      All ingestion pipelines operational
                    </Alert>
                    
                    <VStack spacing={3} align="stretch" width="100%">
                      <HStack justify="space-between">
                        <Text fontSize="sm">CPU Usage</Text>
                        <Text fontSize="sm">67%</Text>
                      </HStack>
                      <Progress value={67} colorScheme="blue" size="sm" />
                      
                      <HStack justify="space-between">
                        <Text fontSize="sm">Memory Usage</Text>
                        <Text fontSize="sm">43%</Text>
                      </HStack>
                      <Progress value={43} colorScheme="green" size="sm" />
                      
                      <HStack justify="space-between">
                        <Text fontSize="sm">Network I/O</Text>
                        <Text fontSize="sm">82%</Text>
                      </HStack>
                      <Progress value={82} colorScheme="yellow" size="sm" />
                    </VStack>
                  </VStack>
                </CardBody>
              </Card>

              <Card bg={cardBg} shadow="md">
                <CardHeader>
                  <Heading size="md">Configuration</Heading>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={3} align="stretch">
                    <HStack justify="space-between">
                      <Text fontSize="sm">Batch Size</Text>
                      <Badge>1000 blocks</Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">Retry Policy</Text>
                      <Badge>Exponential backoff</Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">Buffer Size</Text>
                      <Badge>10MB</Badge>
                    </HStack>
                    <HStack justify="space-between">
                      <Text fontSize="sm">Compression</Text>
                      <Badge colorScheme="green">Enabled (gzip)</Badge>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            </SimpleGrid>

          </VStack>
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default IngestionPage;
