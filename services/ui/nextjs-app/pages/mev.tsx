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
  Alert,
  AlertIcon,
  Code,
} from '@chakra-ui/react';

interface MEVMetrics {
  totalDetected: number;
  sandwichAttacks: number;
  arbitrageOps: number;
  liquidations: number;
  dailyVolume: number;
  alertsTriggered: number;
}

interface MEVAlert {
  id: string;
  type: 'sandwich' | 'arbitrage' | 'liquidation' | 'backrun';
  txHash: string;
  blockNumber: number;
  profit: number;
  victim?: string;
  timestamp: string;
  severity: 'low' | 'medium' | 'high';
}

const MEVPage: NextPage = () => {
  const [metrics, setMetrics] = useState<MEVMetrics>({
    totalDetected: 1247,
    sandwichAttacks: 234,
    arbitrageOps: 456,
    liquidations: 89,
    dailyVolume: 2456789,
    alertsTriggered: 127,
  });

  const [recentAlerts, setRecentAlerts] = useState<MEVAlert[]>([
    {
      id: 'alert1',
      type: 'sandwich',
      txHash: '0x8b4c9f3e2a1d7b6c5e8f9a0d3b2c4e7f1a5b8d9c2e4f7a0b3c5d8f1e4a7b0c3',
      blockNumber: 18756432,
      profit: 2.47,
      victim: '0x742d35Cc8d3C8A9F99D4F7b79Da3E87C1b4b7F8d',
      timestamp: '3 minutes ago',
      severity: 'high',
    },
    {
      id: 'alert2',
      type: 'arbitrage',
      txHash: '0x3a2b1c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890',
      blockNumber: 18756429,
      profit: 0.85,
      timestamp: '7 minutes ago',
      severity: 'medium',
    },
    {
      id: 'alert3',
      type: 'liquidation',
      txHash: '0xdef123456789abcdef123456789abcdef123456789abcdef123456789abcdef12',
      blockNumber: 18756425,
      profit: 1.23,
      victim: '0x8ba1f109edD4bd1C1b8d3C9A2b1c4d5e6f789012',
      timestamp: '12 minutes ago',
      severity: 'medium',
    },
  ]);

  const bgColor = useColorModeValue('gray.100', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalDetected: prev.totalDetected + Math.floor(Math.random() * 3),
        alertsTriggered: prev.alertsTriggered + Math.floor(Math.random() * 2),
        dailyVolume: prev.dailyVolume + Math.floor(Math.random() * 10000),
      }));
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'red';
      case 'medium': return 'yellow';
      case 'low': return 'green';
      default: return 'gray';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'sandwich': return '🥪';
      case 'arbitrage': return '⚖️';
      case 'liquidation': return '💧';
      case 'backrun': return '🏃';
      default: return '🔍';
    }
  };

  return (
    <Box bg={bgColor} minH="100vh">
      <Head>
        <title>MEV Watch Agent | Blockchain Intelligence</title>
        <meta name="description" content="Real-time MEV detection and monitoring system" />
      </Head>

      {/* Header */}
      <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={4} shadow="sm">
        <Container maxW="7xl" px={6}>
          <HStack justify="space-between" align="center">
            <HStack spacing={4}>
              <Link href="/services">
                <Button variant="ghost" size="sm">← All Services</Button>
              </Link>
              <Text fontSize="2xl">🤖</Text>
              <VStack align="start" spacing={0}>
                <Heading size="lg">MEV Watch Agent</Heading>
                <Text color="gray.600">Real-time MEV Detection & Monitoring</Text>
              </VStack>
            </HStack>

            <HStack spacing={3}>
              <Badge colorScheme="green" variant="solid" px={3} py={1}>
                ACTIVE
              </Badge>
              <Badge colorScheme="purple" variant="solid" px={3} py={1}>
                {metrics.alertsTriggered} ALERTS
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
          
          {/* Alert Banner */}
          <Alert status="info" borderRadius="md">
            <AlertIcon />
            <VStack align="start" spacing={1}>
              <Text fontWeight="medium">MEV Watch Agent is actively monitoring Ethereum mainnet</Text>
              <Text fontSize="sm" color="gray.600">
                Detecting sandwich attacks, arbitrage opportunities, and liquidation events in real-time
              </Text>
            </VStack>
          </Alert>

          {/* Metrics Grid */}
          <SimpleGrid columns={{ base: 2, md: 3, lg: 6 }} spacing={4}>
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Total Detected</StatLabel>
                  <StatNumber fontSize="xl">{metrics.totalDetected}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +5.2% this hour
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Sandwich Attacks</StatLabel>
                  <StatNumber fontSize="xl">{metrics.sandwichAttacks}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +8.1% today
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Arbitrage Ops</StatLabel>
                  <StatNumber fontSize="xl">{metrics.arbitrageOps}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +12.3% today
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Liquidations</StatLabel>
                  <StatNumber fontSize="xl">{metrics.liquidations}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="decrease" />
                    -2.4% today
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Daily Volume</StatLabel>
                  <StatNumber fontSize="xl">{(metrics.dailyVolume / 1000000).toFixed(1)}M</StatNumber>
                  <StatHelpText>MEV extracted</StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Alerts</StatLabel>
                  <StatNumber fontSize="xl">{metrics.alertsTriggered}</StatNumber>
                  <StatHelpText>This hour</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Tabs Section */}
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">MEV Monitoring Dashboard</Heading>
            </CardHeader>
            <CardBody>
              <Tabs variant="enclosed">
                <TabList>
                  <Tab>Recent Alerts</Tab>
                  <Tab>Detection Patterns</Tab>
                  <Tab>Agent Configuration</Tab>
                  <Tab>Performance Metrics</Tab>
                </TabList>

                <TabPanels>
                  {/* Recent Alerts Tab */}
                  <TabPanel px={0}>
                    <TableContainer>
                      <Table size="sm">
                        <Thead>
                          <Tr>
                            <Th>Type</Th>
                            <Th>Transaction</Th>
                            <Th>Block</Th>
                            <Th>Profit (ETH)</Th>
                            <Th>Victim</Th>
                            <Th>Severity</Th>
                            <Th>Time</Th>
                          </Tr>
                        </Thead>
                        <Tbody>
                          {recentAlerts.map((alert) => (
                            <Tr key={alert.id}>
                              <Td>
                                <HStack spacing={2}>
                                  <Text>{getTypeIcon(alert.type)}</Text>
                                  <Badge variant="outline" textTransform="capitalize">
                                    {alert.type}
                                  </Badge>
                                </HStack>
                              </Td>
                              <Td>
                                <Code fontSize="xs" colorScheme="blue">
                                  {alert.txHash.slice(0, 10)}...{alert.txHash.slice(-8)}
                                </Code>
                              </Td>
                              <Td>
                                <Text fontFamily="mono" fontSize="sm">
                                  {alert.blockNumber.toLocaleString()}
                                </Text>
                              </Td>
                              <Td>
                                <Text fontWeight="medium" color="green.500">
                                  +{alert.profit.toFixed(2)}
                                </Text>
                              </Td>
                              <Td>
                                {alert.victim ? (
                                  <Code fontSize="xs" colorScheme="red">
                                    {alert.victim.slice(0, 8)}...{alert.victim.slice(-6)}
                                  </Code>
                                ) : (
                                  <Text color="gray.500">-</Text>
                                )}
                              </Td>
                              <Td>
                                <Badge colorScheme={getSeverityColor(alert.severity)} variant="solid">
                                  {alert.severity.toUpperCase()}
                                </Badge>
                              </Td>
                              <Td>
                                <Text fontSize="xs" color="gray.500">
                                  {alert.timestamp}
                                </Text>
                              </Td>
                            </Tr>
                          ))}
                        </Tbody>
                      </Table>
                    </TableContainer>
                  </TabPanel>

                  {/* Detection Patterns Tab */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                      <Card size="sm">
                        <CardHeader pb={2}>
                          <Text fontWeight="medium">Detection Algorithms</Text>
                        </CardHeader>
                        <CardBody pt={0}>
                          <VStack align="stretch" spacing={3}>
                            <HStack justify="space-between">
                              <Text fontSize="sm">🥪 Sandwich Detection</Text>
                              <Badge colorScheme="green">Active</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">⚖️ Arbitrage Monitoring</Text>
                              <Badge colorScheme="green">Active</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">💧 Liquidation Tracker</Text>
                              <Badge colorScheme="green">Active</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">🏃 Backrun Detection</Text>
                              <Badge colorScheme="yellow">Beta</Badge>
                            </HStack>
                          </VStack>
                        </CardBody>
                      </Card>

                      <Card size="sm">
                        <CardHeader pb={2}>
                          <Text fontWeight="medium">Pattern Analysis</Text>
                        </CardHeader>
                        <CardBody pt={0}>
                          <VStack align="stretch" spacing={3}>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Common Patterns</Text>
                              <Text fontSize="sm" fontWeight="medium">15 identified</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Bot Signatures</Text>
                              <Text fontSize="sm" fontWeight="medium">47 tracked</Text>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">False Positives</Text>
                              <Text fontSize="sm" fontWeight="medium">2.3% rate</Text>
                            </HStack>
                          </VStack>
                        </CardBody>
                      </Card>
                    </SimpleGrid>
                  </TabPanel>

                  {/* Configuration Tab */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                      <VStack align="stretch" spacing={4}>
                        <Heading size="sm">Agent Settings</Heading>
                        <Box p={4} border="1px solid" borderColor="gray.200" borderRadius="md">
                          <VStack align="stretch" spacing={3}>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Monitoring Interval</Text>
                              <Badge>1 block</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Alert Threshold</Text>
                              <Badge>0.1 ETH profit</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Network</Text>
                              <Badge colorScheme="blue">Ethereum Mainnet</Badge>
                            </HStack>
                          </VStack>
                        </Box>
                      </VStack>

                      <VStack align="stretch" spacing={4}>
                        <Heading size="sm">Integration Points</Heading>
                        <Box p={4} border="1px solid" borderColor="gray.200" borderRadius="md">
                          <VStack align="stretch" spacing={3}>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Pub/Sub Topic</Text>
                              <Code fontSize="xs">mev-alerts</Code>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">GraphQL API</Text>
                              <Badge colorScheme="green">Connected</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">WebSocket Feed</Text>
                              <Badge colorScheme="green">Active</Badge>
                            </HStack>
                          </VStack>
                        </Box>
                      </VStack>
                    </SimpleGrid>
                  </TabPanel>

                  {/* Performance Metrics Tab */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                      <Card size="sm">
                        <CardBody>
                          <Stat>
                            <StatLabel>Detection Latency</StatLabel>
                            <StatNumber fontSize="lg">45ms</StatNumber>
                            <StatHelpText>Average response time</StatHelpText>
                          </Stat>
                        </CardBody>
                      </Card>
                      
                      <Card size="sm">
                        <CardBody>
                          <Stat>
                            <StatLabel>Accuracy Rate</StatLabel>
                            <StatNumber fontSize="lg">97.7%</StatNumber>
                            <StatHelpText>True positive rate</StatHelpText>
                          </Stat>
                        </CardBody>
                      </Card>

                      <Card size="sm">
                        <CardBody>
                          <Stat>
                            <StatLabel>Uptime</StatLabel>
                            <StatNumber fontSize="lg">99.9%</StatNumber>
                            <StatHelpText>Last 30 days</StatHelpText>
                          </Stat>
                        </CardBody>
                      </Card>
                    </SimpleGrid>
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
                <Button size="sm" variant="outline" leftIcon={<Text>🔔</Text>}>
                  Configure Alerts
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>📊</Text>}>
                  View Analytics
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>⚙️</Text>}>
                  Agent Settings
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>📁</Text>}>
                  Export Data
                </Button>
              </SimpleGrid>
            </CardBody>
          </Card>

        </VStack>
      </Container>
    </Box>
  );
};

export default MEVPage;
