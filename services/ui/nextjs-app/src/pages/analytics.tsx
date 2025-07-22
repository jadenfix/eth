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
  Select,
  Tab,
  Tabs,
  TabList,
  TabPanels,
  TabPanel,
} from '@chakra-ui/react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface AnalyticsMetric {
  name: string;
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
}

const AnalyticsPage: NextPage = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [metrics, setMetrics] = useState<AnalyticsMetric[]>([
    { name: 'Transaction Volume', value: 2456789, change: 12.3, trend: 'up' },
    { name: 'Active Addresses', value: 145678, change: -3.2, trend: 'down' },
    { name: 'Gas Usage', value: 89234567, change: 8.7, trend: 'up' },
    { name: 'MEV Detected', value: 123456, change: 15.8, trend: 'up' },
  ]);

  // Sample data for charts
  const transactionData = [
    { time: '00:00', volume: 45000, count: 2300 },
    { time: '04:00', volume: 52000, count: 2800 },
    { time: '08:00', volume: 78000, count: 4200 },
    { time: '12:00', volume: 95000, count: 5100 },
    { time: '16:00', volume: 88000, count: 4800 },
    { time: '20:00', volume: 67000, count: 3600 },
  ];

  const gasData = [
    { time: '00:00', price: 25, usage: 8500000 },
    { time: '04:00', price: 32, usage: 12000000 },
    { time: '08:00', price: 45, usage: 18000000 },
    { time: '12:00', price: 38, usage: 15000000 },
    { time: '16:00', price: 42, usage: 16500000 },
    { time: '20:00', price: 29, usage: 11000000 },
  ];

  const protocolData = [
    { name: 'Uniswap', value: 35, color: '#FF6B6B' },
    { name: 'OpenSea', value: 22, color: '#4ECDC4' },
    { name: 'Compound', value: 18, color: '#45B7D1' },
    { name: 'Aave', value: 15, color: '#96CEB4' },
    { name: 'Others', value: 10, color: '#FFEAA7' },
  ];

  const bgColor = useColorModeValue('gray.100', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => prev.map(metric => ({
        ...metric,
        value: metric.value + Math.floor(Math.random() * 1000 - 500),
        change: metric.change + (Math.random() - 0.5) * 2,
      })));
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Box bg={bgColor} minH="100vh">
      <Head>
        <title>Analytics Dashboard | Blockchain Intelligence</title>
        <meta name="description" content="Real-time blockchain analytics and insights" />
      </Head>

      {/* Header */}
      <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={4} shadow="sm">
        <Container maxW="7xl" px={6}>
          <HStack justify="space-between" align="center">
            <HStack spacing={4}>
              <Link href="/services">
                <Button variant="ghost" size="sm">← All Services</Button>
              </Link>
              <Text fontSize="2xl">📊</Text>
              <VStack align="start" spacing={0}>
                <Heading size="lg">Analytics Dashboard</Heading>
                <Text color="gray.600">Real-time Blockchain Intelligence</Text>
              </VStack>
            </HStack>

            <HStack spacing={3}>
              <Select value={timeRange} onChange={(e) => setTimeRange(e.target.value)} size="sm" w="auto">
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24h</option>
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
              </Select>
              <Badge colorScheme="green" variant="solid" px={3} py={1}>
                LIVE
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
          
          {/* Key Metrics */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            {metrics.map((metric, idx) => (
              <Card key={idx} bg={cardBg}>
                <CardBody>
                  <Stat>
                    <StatLabel color="gray.600">{metric.name}</StatLabel>
                    <StatNumber fontSize="xl">
                      {metric.name.includes('Volume') || metric.name.includes('Gas') 
                        ? (metric.value / 1000000).toFixed(1) + 'M'
                        : metric.value.toLocaleString()}
                    </StatNumber>
                    <StatHelpText>
                      <StatArrow type={metric.trend === 'up' ? 'increase' : metric.trend === 'down' ? 'decrease' : undefined} />
                      {Math.abs(metric.change).toFixed(1)}% from yesterday
                    </StatHelpText>
                  </Stat>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>

          {/* Charts Section */}
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">Analytics Dashboard</Heading>
            </CardHeader>
            <CardBody>
              <Tabs variant="enclosed">
                <TabList>
                  <Tab>Transaction Analytics</Tab>
                  <Tab>Gas Analytics</Tab>
                  <Tab>Protocol Distribution</Tab>
                  <Tab>Risk Metrics</Tab>
                </TabList>

                <TabPanels>
                  {/* Transaction Analytics */}
                  <TabPanel px={0}>
                    <VStack spacing={6} align="stretch">
                      <Box>
                        <Text mb={4} fontWeight="medium">Transaction Volume Over Time</Text>
                        <Box height="300px">
                          <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={transactionData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="time" />
                              <YAxis />
                              <Tooltip />
                              <Area 
                                type="monotone" 
                                dataKey="volume" 
                                stroke="#4299E1" 
                                fill="#4299E1" 
                                fillOpacity={0.3} 
                              />
                            </AreaChart>
                          </ResponsiveContainer>
                        </Box>
                      </Box>

                      <Box>
                        <Text mb={4} fontWeight="medium">Transaction Count</Text>
                        <Box height="250px">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={transactionData}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="time" />
                              <YAxis />
                              <Tooltip />
                              <Line 
                                type="monotone" 
                                dataKey="count" 
                                stroke="#48BB78" 
                                strokeWidth={2}
                                dot={{ r: 4 }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </Box>
                      </Box>
                    </VStack>
                  </TabPanel>

                  {/* Gas Analytics */}
                  <TabPanel px={0}>
                    <VStack spacing={6} align="stretch">
                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                        <Box>
                          <Text mb={4} fontWeight="medium">Gas Price (Gwei)</Text>
                          <Box height="250px">
                            <ResponsiveContainer width="100%" height="100%">
                              <LineChart data={gasData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="time" />
                                <YAxis />
                                <Tooltip />
                                <Line 
                                  type="monotone" 
                                  dataKey="price" 
                                  stroke="#F56565" 
                                  strokeWidth={3}
                                />
                              </LineChart>
                            </ResponsiveContainer>
                          </Box>
                        </Box>

                        <Box>
                          <Text mb={4} fontWeight="medium">Gas Usage</Text>
                          <Box height="250px">
                            <ResponsiveContainer width="100%" height="100%">
                              <BarChart data={gasData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="time" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="usage" fill="#9F7AEA" />
                              </BarChart>
                            </ResponsiveContainer>
                          </Box>
                        </Box>
                      </SimpleGrid>
                    </VStack>
                  </TabPanel>

                  {/* Protocol Distribution */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                      <Box>
                        <Text mb={4} fontWeight="medium">Top Protocols by Volume</Text>
                        <Box height="300px">
                          <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                              <Pie
                                data={protocolData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={120}
                                paddingAngle={5}
                                dataKey="value"
                              >
                                {protocolData.map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                              </Pie>
                              <Tooltip />
                            </PieChart>
                          </ResponsiveContainer>
                        </Box>
                      </Box>

                      <Box>
                        <Text mb={4} fontWeight="medium">Protocol Statistics</Text>
                        <VStack spacing={3} align="stretch">
                          {protocolData.map((protocol, idx) => (
                            <HStack key={idx} justify="space-between" p={3} border="1px solid" borderColor="gray.200" borderRadius="md">
                              <HStack spacing={3}>
                                <Box w={3} h={3} bg={protocol.color} borderRadius="full" />
                                <Text fontWeight="medium">{protocol.name}</Text>
                              </HStack>
                              <VStack align="end" spacing={1}>
                                <Text fontWeight="bold">{protocol.value}%</Text>
                                <Progress value={protocol.value} size="sm" width="60px" />
                              </VStack>
                            </HStack>
                          ))}
                        </VStack>
                      </Box>
                    </SimpleGrid>
                  </TabPanel>

                  {/* Risk Metrics */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                      <Card size="sm">
                        <CardHeader pb={2}>
                          <Text fontWeight="medium">Risk Distribution</Text>
                        </CardHeader>
                        <CardBody pt={0}>
                          <VStack spacing={3}>
                            <HStack justify="space-between" w="100%">
                              <Text fontSize="sm">Low Risk</Text>
                              <HStack spacing={2}>
                                <Progress value={75} size="sm" width="100px" colorScheme="green" />
                                <Text fontSize="sm" fontWeight="medium">75%</Text>
                              </HStack>
                            </HStack>
                            <HStack justify="space-between" w="100%">
                              <Text fontSize="sm">Medium Risk</Text>
                              <HStack spacing={2}>
                                <Progress value={20} size="sm" width="100px" colorScheme="yellow" />
                                <Text fontSize="sm" fontWeight="medium">20%</Text>
                              </HStack>
                            </HStack>
                            <HStack justify="space-between" w="100%">
                              <Text fontSize="sm">High Risk</Text>
                              <HStack spacing={2}>
                                <Progress value={5} size="sm" width="100px" colorScheme="red" />
                                <Text fontSize="sm" fontWeight="medium">5%</Text>
                              </HStack>
                            </HStack>
                          </VStack>
                        </CardBody>
                      </Card>

                      <Card size="sm">
                        <CardHeader pb={2}>
                          <Text fontWeight="medium">Anomaly Detection</Text>
                        </CardHeader>
                        <CardBody pt={0}>
                          <VStack spacing={3} align="stretch">
                            <HStack justify="space-between">
                              <Text fontSize="sm">Suspicious Transactions</Text>
                              <Badge colorScheme="red" variant="solid">234</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Large Transfers</Text>
                              <Badge colorScheme="orange" variant="solid">89</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">MEV Activities</Text>
                              <Badge colorScheme="purple" variant="solid">156</Badge>
                            </HStack>
                            <HStack justify="space-between">
                              <Text fontSize="sm">Flash Loans</Text>
                              <Badge colorScheme="blue" variant="solid">45</Badge>
                            </HStack>
                          </VStack>
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
                <Button size="sm" variant="outline" leftIcon={<Text>📈</Text>}>
                  Export Data
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>⚙️</Text>}>
                  Configure Alerts
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>🔍</Text>}>
                  Deep Dive Analysis
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>📊</Text>}>
                  Create Report
                </Button>
              </SimpleGrid>
            </CardBody>
          </Card>

        </VStack>
      </Container>
    </Box>
  );
};

export default AnalyticsPage;
