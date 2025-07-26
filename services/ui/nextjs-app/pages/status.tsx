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
  Tab,
  Tabs,
  TabList,
  TabPanels,
  TabPanel,
  List,
  ListItem,
  ListIcon,
  Alert,
  AlertIcon,
  CircularProgress,
  CircularProgressLabel,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon, TimeIcon } from '@chakra-ui/icons';
import { ResponsiveLayout } from '../src/components';

interface ServiceHealth {
  id: string;
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  uptime: number;
  responseTime: number;
  lastCheck: string;
  endpoint: string;
}

interface SystemMetrics {
  totalRequests: number;
  avgResponseTime: number;
  errorRate: number;
  activeConnections: number;
  cpuUsage: number;
  memoryUsage: number;
}

const StatusDashboardPage: NextPage = () => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    totalRequests: 145678,
    avgResponseTime: 125,
    errorRate: 0.23,
    activeConnections: 2456,
    cpuUsage: 34.5,
    memoryUsage: 67.8,
  });

  const [services, setServices] = useState<ServiceHealth[]>([
    {
      id: 'ingestion',
      name: 'Data Ingestion',
      status: 'healthy',
      uptime: 99.9,
      responseTime: 45,
      lastCheck: '30 seconds ago',
      endpoint: '/health/ingestion'
    },
    {
      id: 'ontology',
      name: 'Ontology Service',
      status: 'healthy',
      uptime: 99.8,
      responseTime: 78,
      lastCheck: '30 seconds ago',
      endpoint: '/health/ontology'
    },
    {
      id: 'mev-agent',
      name: 'MEV Watch Agent',
      status: 'healthy',
      uptime: 99.95,
      responseTime: 23,
      lastCheck: '30 seconds ago',
      endpoint: '/health/mev'
    },
    {
      id: 'api-gateway',
      name: 'API Gateway',
      status: 'degraded',
      uptime: 97.2,
      responseTime: 245,
      lastCheck: '35 seconds ago',
      endpoint: '/health/api'
    },
    {
      id: 'graph-api',
      name: 'Graph API',
      status: 'healthy',
      uptime: 99.7,
      responseTime: 89,
      lastCheck: '28 seconds ago',
      endpoint: '/health/graph'
    },
    {
      id: 'voiceops',
      name: 'VoiceOps Service',
      status: 'down',
      uptime: 85.4,
      responseTime: 0,
      lastCheck: '5 minutes ago',
      endpoint: '/health/voice'
    },
  ]);

  const bgColor = useColorModeValue('gray.100', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics(prev => ({
        ...prev,
        totalRequests: prev.totalRequests + Math.floor(Math.random() * 100),
        avgResponseTime: prev.avgResponseTime + (Math.random() - 0.5) * 10,
        activeConnections: prev.activeConnections + Math.floor(Math.random() * 20 - 10),
        cpuUsage: Math.max(10, Math.min(90, prev.cpuUsage + (Math.random() - 0.5) * 5)),
        memoryUsage: Math.max(30, Math.min(95, prev.memoryUsage + (Math.random() - 0.5) * 3)),
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'green';
      case 'degraded': return 'yellow';
      case 'down': return 'red';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return CheckCircleIcon;
      case 'degraded': return WarningIcon;
      case 'down': return TimeIcon;
      default: return CheckCircleIcon;
    }
  };

  const overallHealth = services.filter(s => s.status === 'healthy').length / services.length * 100;

  return (
    <ResponsiveLayout 
      title="Status Dashboard | System Health"
      description="Real-time system health and operational metrics"
    >
      <Head>
        <title>Status Dashboard | System Health</title>
        <meta name="description" content="Real-time system health and operational metrics" />
      </Head>

      <Box bg={bgColor} minH="100vh">

      {/* Header */}
      <Box bg={cardBg} borderBottom="1px solid" borderColor="gray.200" py={4} shadow="sm">
        <Container maxW="7xl" px={6}>
          <HStack justify="space-between" align="center">
            <HStack spacing={4}>
              <Link href="/services">
                <Button variant="ghost" size="sm">← All Services</Button>
              </Link>
              <Text fontSize="2xl">📋</Text>
              <VStack align="start" spacing={0}>
                <Heading size="lg">Status Dashboard</Heading>
                <Text color="gray.600">System Health & Operational Metrics</Text>
              </VStack>
            </HStack>

            <HStack spacing={3}>
              <Badge 
                colorScheme={overallHealth > 90 ? 'green' : overallHealth > 70 ? 'yellow' : 'red'} 
                variant="solid" 
                px={3} 
                py={1}
              >
                {overallHealth.toFixed(1)}% HEALTHY
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
          
          {/* System Status Alert */}
          {overallHealth < 90 && (
            <Alert status="warning" borderRadius="md">
              <AlertIcon />
              <VStack align="start" spacing={1}>
                <Text fontWeight="medium">System Degradation Detected</Text>
                <Text fontSize="sm" color="gray.600">
                  Some services are experiencing issues. Check individual service status below.
                </Text>
              </VStack>
            </Alert>
          )}

          {/* Overall System Health */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            <Card bg={cardBg}>
              <CardBody display="flex" alignItems="center" justifyContent="center">
                <VStack spacing={3}>
                  <CircularProgress 
                    value={overallHealth} 
                    size="80px" 
                    color={overallHealth > 90 ? 'green.400' : overallHealth > 70 ? 'yellow.400' : 'red.400'}
                  >
                    <CircularProgressLabel fontSize="sm" fontWeight="bold">
                      {overallHealth.toFixed(0)}%
                    </CircularProgressLabel>
                  </CircularProgress>
                  <Text fontSize="sm" fontWeight="medium">Overall Health</Text>
                </VStack>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Total Requests</StatLabel>
                  <StatNumber fontSize="xl">{systemMetrics.totalRequests.toLocaleString()}</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    +12.5% this hour
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Avg Response Time</StatLabel>
                  <StatNumber fontSize="xl">{Math.round(systemMetrics.avgResponseTime)}ms</StatNumber>
                  <StatHelpText>
                    <StatArrow type={systemMetrics.avgResponseTime < 150 ? 'decrease' : 'increase'} />
                    Target: &lt;150ms
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel color="gray.600">Error Rate</StatLabel>
                  <StatNumber fontSize="xl">{systemMetrics.errorRate.toFixed(2)}%</StatNumber>
                  <StatHelpText>
                    <StatArrow type={systemMetrics.errorRate < 1 ? 'decrease' : 'increase'} />
                    Last 24 hours
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Resource Usage */}
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            <Card bg={cardBg}>
              <CardHeader>
                <Heading size="sm">CPU Usage</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={3}>
                  <Progress 
                    value={systemMetrics.cpuUsage} 
                    size="lg" 
                    width="100%"
                    colorScheme={systemMetrics.cpuUsage < 70 ? 'green' : systemMetrics.cpuUsage < 85 ? 'yellow' : 'red'}
                  />
                  <HStack justify="space-between" width="100%">
                    <Text fontSize="sm" color="gray.600">Current: {systemMetrics.cpuUsage.toFixed(1)}%</Text>
                    <Text fontSize="sm" color="gray.600">Target: &lt;70%</Text>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>

            <Card bg={cardBg}>
              <CardHeader>
                <Heading size="sm">Memory Usage</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={3}>
                  <Progress 
                    value={systemMetrics.memoryUsage} 
                    size="lg" 
                    width="100%"
                    colorScheme={systemMetrics.memoryUsage < 80 ? 'green' : systemMetrics.memoryUsage < 90 ? 'yellow' : 'red'}
                  />
                  <HStack justify="space-between" width="100%">
                    <Text fontSize="sm" color="gray.600">Current: {systemMetrics.memoryUsage.toFixed(1)}%</Text>
                    <Text fontSize="sm" color="gray.600">Target: &lt;80%</Text>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Service Status */}
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">Service Health Status</Heading>
            </CardHeader>
            <CardBody>
              <Tabs variant="enclosed">
                <TabList>
                  <Tab>All Services</Tab>
                  <Tab>Incidents</Tab>
                  <Tab>Performance</Tab>
                  <Tab>Configuration</Tab>
                </TabList>

                <TabPanels>
                  {/* All Services Tab */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                      {services.map((service) => (
                        <Card key={service.id} size="sm" variant="outline">
                          <CardBody>
                            <VStack align="stretch" spacing={3}>
                              <HStack justify="space-between">
                                <HStack spacing={2}>
                                  <Box as={getStatusIcon(service.status)} 
                                    color={`${getStatusColor(service.status)}.500`} 
                                  />
                                  <Text fontWeight="medium">{service.name}</Text>
                                </HStack>
                                <Badge colorScheme={getStatusColor(service.status)} variant="solid">
                                  {service.status.toUpperCase()}
                                </Badge>
                              </HStack>
                              
                              <SimpleGrid columns={3} spacing={2}>
                                <VStack spacing={1}>
                                  <Text fontSize="xs" color="gray.600">Uptime</Text>
                                  <Text fontSize="sm" fontWeight="medium">{service.uptime}%</Text>
                                </VStack>
                                <VStack spacing={1}>
                                  <Text fontSize="xs" color="gray.600">Response</Text>
                                  <Text fontSize="sm" fontWeight="medium">{service.responseTime}ms</Text>
                                </VStack>
                                <VStack spacing={1}>
                                  <Text fontSize="xs" color="gray.600">Last Check</Text>
                                  <Text fontSize="xs">{service.lastCheck}</Text>
                                </VStack>
                              </SimpleGrid>
                              
                              <Progress 
                                value={service.uptime} 
                                size="sm"
                                colorScheme={service.uptime > 99 ? 'green' : service.uptime > 95 ? 'yellow' : 'red'}
                              />
                            </VStack>
                          </CardBody>
                        </Card>
                      ))}
                    </SimpleGrid>
                  </TabPanel>

                  {/* Incidents Tab */}
                  <TabPanel px={0}>
                    <VStack spacing={4} align="stretch">
                      <Text color="gray.600">Recent incidents and service interruptions</Text>
                      
                      <List spacing={3}>
                        <ListItem>
                          <HStack spacing={3}>
                            <Box as={WarningIcon} color="yellow.500" />
                            <VStack align="start" spacing={1} flex={1}>
                              <HStack justify="space-between" width="100%">
                                <Text fontWeight="medium">API Gateway Degradation</Text>
                                <Text fontSize="sm" color="gray.500">45 minutes ago</Text>
                              </HStack>
                              <Text fontSize="sm" color="gray.600">
                                Elevated response times detected on /api/v1 endpoints
                              </Text>
                            </VStack>
                          </HStack>
                        </ListItem>

                        <ListItem>
                          <HStack spacing={3}>
                            <Box as={TimeIcon} color="red.500" />
                            <VStack align="start" spacing={1} flex={1}>
                              <HStack justify="space-between" width="100%">
                                <Text fontWeight="medium">VoiceOps Service Outage</Text>
                                <Text fontSize="sm" color="gray.500">2 hours ago</Text>
                              </HStack>
                              <Text fontSize="sm" color="gray.600">
                                Service unavailable due to ElevenLabs API issues
                              </Text>
                            </VStack>
                          </HStack>
                        </ListItem>

                        <ListItem>
                          <HStack spacing={3}>
                            <Box as={CheckCircleIcon} color="green.500" />
                            <VStack align="start" spacing={1} flex={1}>
                              <HStack justify="space-between" width="100%">
                                <Text fontWeight="medium">Database Maintenance Completed</Text>
                                <Text fontSize="sm" color="gray.500">6 hours ago</Text>
                              </HStack>
                              <Text fontSize="sm" color="gray.600">
                                Scheduled Neo4j maintenance completed successfully
                              </Text>
                            </VStack>
                          </HStack>
                        </ListItem>
                      </List>
                    </VStack>
                  </TabPanel>

                  {/* Performance Tab */}
                  <TabPanel px={0}>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                      <VStack align="stretch" spacing={4}>
                        <Heading size="sm">Response Time Metrics</Heading>
                        {services.map((service) => (
                          <HStack key={service.id} justify="space-between">
                            <Text fontSize="sm">{service.name}</Text>
                            <HStack spacing={2}>
                              <Text fontSize="sm" fontWeight="medium">{service.responseTime}ms</Text>
                              <Progress 
                                value={Math.min(100, service.responseTime / 2)} 
                                size="sm" 
                                width="60px"
                                colorScheme={service.responseTime < 100 ? 'green' : service.responseTime < 200 ? 'yellow' : 'red'}
                              />
                            </HStack>
                          </HStack>
                        ))}
                      </VStack>

                      <VStack align="stretch" spacing={4}>
                        <Heading size="sm">Uptime Statistics</Heading>
                        {services.map((service) => (
                          <HStack key={service.id} justify="space-between">
                            <Text fontSize="sm">{service.name}</Text>
                            <HStack spacing={2}>
                              <Text fontSize="sm" fontWeight="medium">{service.uptime}%</Text>
                              <Progress 
                                value={service.uptime} 
                                size="sm" 
                                width="60px"
                                colorScheme={service.uptime > 99 ? 'green' : service.uptime > 95 ? 'yellow' : 'red'}
                              />
                            </HStack>
                          </HStack>
                        ))}
                      </VStack>
                    </SimpleGrid>
                  </TabPanel>

                  {/* Configuration Tab */}
                  <TabPanel px={0}>
                    <VStack spacing={4} align="stretch">
                      <Text color="gray.600">Health check configuration and monitoring settings</Text>
                      
                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                        <Card size="sm">
                          <CardHeader pb={2}>
                            <Text fontWeight="medium">Check Intervals</Text>
                          </CardHeader>
                          <CardBody pt={0}>
                            <VStack align="stretch" spacing={2}>
                              <HStack justify="space-between">
                                <Text fontSize="sm">Health Checks</Text>
                                <Badge>30s</Badge>
                              </HStack>
                              <HStack justify="space-between">
                                <Text fontSize="sm">Performance Metrics</Text>
                                <Badge>5s</Badge>
                              </HStack>
                              <HStack justify="space-between">
                                <Text fontSize="sm">Incident Detection</Text>
                                <Badge>1s</Badge>
                              </HStack>
                            </VStack>
                          </CardBody>
                        </Card>

                        <Card size="sm">
                          <CardHeader pb={2}>
                            <Text fontWeight="medium">Alert Thresholds</Text>
                          </CardHeader>
                          <CardBody pt={0}>
                            <VStack align="stretch" spacing={2}>
                              <HStack justify="space-between">
                                <Text fontSize="sm">Response Time</Text>
                                <Badge colorScheme="yellow">&gt;200ms</Badge>
                              </HStack>
                              <HStack justify="space-between">
                                <Text fontSize="sm">Error Rate</Text>
                                <Badge colorScheme="red">&gt;1%</Badge>
                              </HStack>
                              <HStack justify="space-between">
                                <Text fontSize="sm">Uptime</Text>
                                <Badge colorScheme="orange">&lt;95%</Badge>
                              </HStack>
                            </VStack>
                          </CardBody>
                        </Card>
                      </SimpleGrid>
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
                <Button size="sm" variant="outline" leftIcon={<Text>🔄</Text>}>
                  Refresh All
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>⚙️</Text>}>
                  Configure Alerts
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>📊</Text>}>
                  View Logs
                </Button>
                <Button size="sm" variant="outline" leftIcon={<Text>📁</Text>}>
                  Export Report
                </Button>
              </SimpleGrid>
            </CardBody>
          </Card>

        </VStack>
      </Container>
    </Box>
    </ResponsiveLayout>
  );
};

export default StatusDashboardPage;
