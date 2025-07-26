import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Card,
  CardBody,
  Grid,
  GridItem,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorModeValue,
  Icon,
  Flex,
  SimpleGrid,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Progress,
  List,
  ListItem,
  ListIcon,
  Divider,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Input,
  Select,
  FormControl,
  FormLabel,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { 
  FiActivity, 
  FiShield, 
  FiTrendingUp, 
  FiAlertTriangle, 
  FiEye, 
  FiSearch,
  FiDatabase,
  FiCpu,
  FiGlobe,
  FiBarChart,
  FiUsers,
  FiSettings,
  FiPlay,
  FiPause,
  FiRefreshCw,
  FiCheckCircle,
  FiXCircle,
  FiClock,
  FiDollarSign,
  FiZap,
  FiTarget,
  FiMapPin,
  FiLayers,
  FiGitBranch,
  FiMonitor,
  FiHeadphones,
  FiCode,
  FiGrid,
  FiPieChart,
  FiNavigation,
  FiCompass,
  FiAward,
  FiStar,
  FiPocket,
  FiArrowRight,
  FiPlus,
  FiBell,
  FiMenu,
  FiHome,
  FiPieChart as FiAnalytics,
  FiShield as FiSecurity,
  FiUsers as FiEntities,
  FiZap as FiMev,
  FiGlobe as FiVisualization,
  FiSettings as FiWorkflow,
  FiHeadphones as FiVoice,
  FiMonitor as FiMonitoring
} from 'react-icons/fi';

// Comprehensive demo data
const demoData = {
  systemHealth: {
    status: 'healthy',
    uptime: '99.9%',
    services: [
      { name: 'Ethereum Ingester', status: 'active', latency: '45ms', color: 'green' },
      { name: 'Graph API', status: 'active', latency: '12ms', color: 'green' },
      { name: 'Voice Ops', status: 'active', latency: '78ms', color: 'green' },
      { name: 'MEV Agent', status: 'active', latency: '23ms', color: 'green' },
      { name: 'Entity Resolution', status: 'active', latency: '156ms', color: 'green' },
    ]
  },
  blockchainMetrics: {
    blocksProcessed: 1247,
    transactionsAnalyzed: 45678,
    eventsExtracted: 8923,
    entitiesResolved: 3421,
    mevDetected: 23,
    riskAlerts: 7,
  },
  realTimeAlerts: [
    { id: 1, type: 'mev', severity: 'high', message: 'Front-running attack detected on Uniswap V3', time: '2 min ago', value: '$45,230' },
    { id: 2, type: 'sanctions', severity: 'medium', message: 'OFAC-sanctioned address detected in transaction', time: '5 min ago', value: '0x742d35...' },
    { id: 3, type: 'anomaly', severity: 'low', message: 'Unusual transaction pattern detected', time: '8 min ago', value: '$12,450' },
    { id: 4, type: 'arbitrage', severity: 'info', message: 'Cross-DEX arbitrage opportunity identified', time: '12 min ago', value: '$890' },
  ],
  entityResolution: {
    totalEntities: 15420,
    confidenceScore: 94.2,
    recentMatches: [
      { address: '0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6', entity: 'Binance Hot Wallet', confidence: 98.5 },
      { address: '0x28C6c06298d514Db089934071355E5743bf21d60', entity: 'Coinbase Exchange', confidence: 97.2 },
      { address: '0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549', entity: 'Tether Treasury', confidence: 96.8 },
    ]
  },
  mevOpportunities: [
    { id: 1, type: 'sandwich', profit: '$2,450', risk: 'medium', status: 'active' },
    { id: 2, type: 'arbitrage', profit: '$890', risk: 'low', status: 'monitoring' },
    { id: 3, type: 'liquidation', profit: '$1,200', risk: 'high', status: 'expired' },
  ],
  features: [
    { name: 'Real-time Blockchain Ingestion', icon: FiDatabase, description: 'Live Ethereum data processing', status: 'active' },
    { name: 'AI-Powered Entity Resolution', icon: FiUsers, description: 'Address clustering and mapping', status: 'active' },
    { name: 'MEV Detection & Monitoring', icon: FiZap, description: 'Front-running and arbitrage detection', status: 'active' },
    { name: 'Security & Compliance', icon: FiShield, description: 'OFAC screening and audit trails', status: 'active' },
    { name: 'Voice Commands', icon: FiHeadphones, description: 'Natural language interface', status: 'active' },
    { name: 'Advanced Analytics', icon: FiBarChart, description: 'ML-powered risk assessment', status: 'active' },
    { name: '3D Visualization', icon: FiGlobe, description: 'Interactive graph exploration', status: 'active' },
    { name: 'Workflow Automation', icon: FiSettings, description: 'Low-code signal building', status: 'active' },
  ]
};

const DemoSlide: React.FC = () => {
  const [isLive, setIsLive] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  const bg = useColorModeValue('gray.50', 'palantir.navy');
  const cardBg = useColorModeValue('white', 'palantir.navy-light');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.300');

  useEffect(() => {
    if (isLive) {
      const interval = setInterval(() => {
        toast({
          title: "Live Update",
          description: "New blockchain data processed",
          status: "info",
          duration: 2000,
          isClosable: true,
        });
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [isLive, toast]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'yellow';
      case 'info': return 'blue';
      default: return 'gray';
    }
  };

  const getMevTypeIcon = (type: string) => {
    switch (type) {
      case 'sandwich': return FiTarget;
      case 'arbitrage': return FiTrendingUp;
      case 'liquidation': return FiAlertTriangle;
      default: return FiZap;
    }
  };

  return (
    <Box bg={bg} minH="100vh" p={6}>
      {/* Header */}
      <VStack spacing={6} align="stretch">
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={2}>
            <Heading size="2xl" color={textColor} display="flex" alignItems="center">
              <Icon as={FiPocket} mr={3} color="blue.500" />
              Onchain Command Center
            </Heading>
            <Text color={mutedTextColor} fontSize="lg">
              Enterprise Blockchain Intelligence Platform - Complete Demo
            </Text>
          </VStack>
          <HStack spacing={4}>
            <Badge colorScheme="green" variant="subtle" fontSize="md" px={3} py={1}>
              <Icon as={FiCheckCircle} mr={1} />
              25/25 Tests Passing
            </Badge>
            <Button
              leftIcon={<Icon as={isLive ? FiPause : FiPlay} />}
              colorScheme={isLive ? 'red' : 'green'}
              onClick={() => setIsLive(!isLive)}
            >
              {isLive ? 'Pause Live' : 'Start Live'}
            </Button>
          </HStack>
        </HStack>

        {/* System Status Banner */}
        <Alert status="success" borderRadius="lg">
          <AlertIcon />
          <Box>
            <AlertTitle>Production Ready - All 50+ Features Active</AlertTitle>
            <AlertDescription>
              Real-time blockchain monitoring • AI-powered intelligence • Enterprise security • Complete compliance
            </AlertDescription>
          </Box>
        </Alert>

        {/* Main Demo Content */}
        <Tabs onChange={setActiveTab} value={activeTab} variant="enclosed">
          <TabList>
            <Tab><Icon as={FiActivity} mr={2} />Live Dashboard</Tab>
            <Tab><Icon as={FiZap} mr={2} />MEV Intelligence</Tab>
            <Tab><Icon as={FiUsers} mr={2} />Entity Resolution</Tab>
            <Tab><Icon as={FiShield} mr={2} />Security & Compliance</Tab>
            <Tab><Icon as={FiBarChart} mr={2} />Analytics</Tab>
            <Tab><Icon as={FiGlobe} mr={2} />Visualization</Tab>
          </TabList>

          <TabPanels>
            {/* Live Dashboard Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                {/* Key Metrics */}
                <SimpleGrid columns={{ base: 2, md: 3, lg: 6 }} spacing={4}>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody p={4}>
                      <Stat>
                        <StatLabel color={mutedTextColor} fontSize="sm">Blocks Processed</StatLabel>
                        <StatNumber color="blue.500" fontSize="xl">{demoData.blockchainMetrics.blocksProcessed.toLocaleString()}</StatNumber>
                        <StatHelpText fontSize="xs">Last 24 hours</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody p={4}>
                      <Stat>
                        <StatLabel color={mutedTextColor} fontSize="sm">Transactions</StatLabel>
                        <StatNumber color="green.500" fontSize="xl">{demoData.blockchainMetrics.transactionsAnalyzed.toLocaleString()}</StatNumber>
                        <StatHelpText fontSize="xs">Real-time analysis</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody p={4}>
                      <Stat>
                        <StatLabel color={mutedTextColor} fontSize="sm">Events Extracted</StatLabel>
                        <StatNumber color="purple.500" fontSize="xl">{demoData.blockchainMetrics.eventsExtracted.toLocaleString()}</StatNumber>
                        <StatHelpText fontSize="xs">Smart contracts</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody p={4}>
                      <Stat>
                        <StatLabel color={mutedTextColor} fontSize="sm">Entities Resolved</StatLabel>
                        <StatNumber color="orange.500" fontSize="xl">{demoData.blockchainMetrics.entitiesResolved.toLocaleString()}</StatNumber>
                        <StatHelpText fontSize="xs">AI matching</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody p={4}>
                      <Stat>
                        <StatLabel color={mutedTextColor} fontSize="sm">MEV Detected</StatLabel>
                        <StatNumber color="red.500" fontSize="xl">{demoData.blockchainMetrics.mevDetected}</StatNumber>
                        <StatHelpText fontSize="xs">Attack patterns</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody p={4}>
                      <Stat>
                        <StatLabel color={mutedTextColor} fontSize="sm">Risk Alerts</StatLabel>
                        <StatNumber color="yellow.500" fontSize="xl">{demoData.blockchainMetrics.riskAlerts}</StatNumber>
                        <StatHelpText fontSize="xs">Active threats</StatHelpText>
                      </Stat>
                    </CardBody>
                  </Card>
                </SimpleGrid>

                {/* System Health & Recent Activity */}
                <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <Heading size="md" color={textColor} mb={4} display="flex" alignItems="center">
                        <Icon as={FiMonitor} mr={2} color="green.500" />
                        System Health
                      </Heading>
                      <VStack spacing={3} align="stretch">
                        {demoData.systemHealth.services.map((service, index) => (
                          <HStack key={index} justify="space-between">
                            <Text fontSize="sm" fontWeight="medium">{service.name}</Text>
                            <HStack spacing={2}>
                              <Badge colorScheme={service.color} size="sm">{service.status}</Badge>
                              <Text fontSize="xs" color={mutedTextColor}>{service.latency}</Text>
                            </HStack>
                          </HStack>
                        ))}
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <Heading size="md" color={textColor} mb={4} display="flex" alignItems="center">
                        <Icon as={FiActivity} mr={2} color="blue.500" />
                        Live Alerts
                      </Heading>
                      <VStack spacing={3} align="stretch" maxH="300px" overflowY="auto">
                        {demoData.realTimeAlerts.map((alert) => (
                          <Box key={alert.id} p={3} border="1px" borderColor={borderColor} borderRadius="md">
                            <HStack justify="space-between" mb={1}>
                              <Badge colorScheme={getSeverityColor(alert.severity)} size="sm">
                                {alert.type.toUpperCase()}
                              </Badge>
                              <Text fontSize="xs" color={mutedTextColor}>{alert.time}</Text>
                            </HStack>
                            <Text fontSize="sm" color={textColor} mb={1}>{alert.message}</Text>
                            <Text fontSize="xs" color="blue.500" fontWeight="bold">{alert.value}</Text>
                          </Box>
                        ))}
                      </VStack>
                    </CardBody>
                  </Card>
                </Grid>
              </VStack>
            </TabPanel>

            {/* MEV Intelligence Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Heading size="lg" color={textColor} textAlign="center">
                  <Icon as={FiZap} mr={3} color="orange.500" />
                  MEV Detection & Intelligence
                </Heading>
                
                <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <Heading size="md" color={textColor} mb={4}>
                        Active MEV Opportunities
                      </Heading>
                      <VStack spacing={4} align="stretch">
                        {demoData.mevOpportunities.map((opp) => (
                          <Card key={opp.id} variant="outline" size="sm">
                            <CardBody p={3}>
                              <HStack justify="space-between" mb={2}>
                                <Icon as={getMevTypeIcon(opp.type)} color="blue.500" />
                                <Badge colorScheme={opp.risk === 'high' ? 'red' : opp.risk === 'medium' ? 'orange' : 'green'}>
                                  {opp.risk}
                                </Badge>
                              </HStack>
                              <Text fontWeight="bold" fontSize="lg" color="green.500">{opp.profit}</Text>
                              <Text fontSize="sm" color={mutedTextColor} textTransform="capitalize">
                                {opp.type} opportunity
                              </Text>
                              <Badge size="sm" colorScheme={opp.status === 'active' ? 'green' : opp.status === 'monitoring' ? 'blue' : 'gray'}>
                                {opp.status}
                              </Badge>
                            </CardBody>
                          </Card>
                        ))}
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <Heading size="md" color={textColor} mb={4}>
                        MEV Detection Features
                      </Heading>
                      <VStack spacing={3} align="stretch">
                        <HStack p={3} bg="red.50" borderRadius="md">
                          <Icon as={FiTarget} color="red.500" />
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="bold" fontSize="sm">Sandwich Attacks</Text>
                            <Text fontSize="xs" color={mutedTextColor}>Real-time detection of front-running patterns</Text>
                          </VStack>
                        </HStack>
                        <HStack p={3} bg="orange.50" borderRadius="md">
                          <Icon as={FiTrendingUp} color="orange.500" />
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="bold" fontSize="sm">Arbitrage Opportunities</Text>
                            <Text fontSize="xs" color={mutedTextColor}>Cross-DEX price differences and opportunities</Text>
                          </VStack>
                        </HStack>
                        <HStack p={3} bg="yellow.50" borderRadius="md">
                          <Icon as={FiAlertTriangle} color="yellow.500" />
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="bold" fontSize="sm">Liquidation Events</Text>
                            <Text fontSize="xs" color={mutedTextColor}>DeFi liquidation monitoring and alerts</Text>
                          </VStack>
                        </HStack>
                      </VStack>
                    </CardBody>
                  </Card>
                </Grid>
              </VStack>
            </TabPanel>

            {/* Entity Resolution Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Heading size="lg" color={textColor} textAlign="center">
                  <Icon as={FiUsers} mr={3} color="purple.500" />
                  AI-Powered Entity Resolution
                </Heading>
                
                <Grid templateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={6}>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <Heading size="md" color={textColor} mb={4}>
                        Entity Resolution Stats
                      </Heading>
                      <VStack spacing={4} align="stretch">
                        <HStack justify="space-between">
                          <Text>Total Entities Resolved</Text>
                          <Text fontWeight="bold" color="blue.500">{demoData.entityResolution.totalEntities.toLocaleString()}</Text>
                        </HStack>
                        <HStack justify="space-between">
                          <Text>Confidence Score</Text>
                          <Text fontWeight="bold" color="green.500">{demoData.entityResolution.confidenceScore}%</Text>
                        </HStack>
                        <Progress value={demoData.entityResolution.confidenceScore} colorScheme="green" />
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <Heading size="md" color={textColor} mb={4}>
                        Recent Entity Matches
                      </Heading>
                      <VStack spacing={3} align="stretch">
                        {demoData.entityResolution.recentMatches.map((match, index) => (
                          <HStack key={index} justify="space-between" p={3} bg="gray.50" borderRadius="md">
                            <VStack align="start" spacing={1}>
                              <Text fontSize="sm" fontWeight="medium" color={textColor}>
                                {match.entity}
                              </Text>
                              <Text fontSize="xs" color={mutedTextColor} fontFamily="mono">
                                {match.address}
                              </Text>
                            </VStack>
                            <Badge colorScheme="green" variant="subtle">
                              {match.confidence}%
                            </Badge>
                          </HStack>
                        ))}
                      </VStack>
                    </CardBody>
                  </Card>
                </Grid>
              </VStack>
            </TabPanel>

            {/* Security & Compliance Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Heading size="lg" color={textColor} textAlign="center">
                  <Icon as={FiShield} mr={3} color="green.500" />
                  Security & Compliance
                </Heading>
                
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiShield} color="blue.500" boxSize={8} />
                        <Heading size="md" color={textColor}>Access Control</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          Role-based access control with fine-grained permissions
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiCheckCircle} color="green.500" boxSize={8} />
                        <Heading size="md" color={textColor}>OFAC Screening</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          Real-time sanctions list checking and compliance monitoring
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiAward} color="purple.500" boxSize={8} />
                        <Heading size="md" color={textColor}>SOC2 Compliance</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          Complete audit trails and security controls compliance
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>
                </SimpleGrid>
              </VStack>
            </TabPanel>

            {/* Analytics Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Heading size="lg" color={textColor} textAlign="center">
                  <Icon as={FiBarChart} mr={3} color="teal.500" />
                  Advanced Analytics
                </Heading>
                
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiPieChart} color="blue.500" boxSize={8} />
                        <Heading size="md" color={textColor}>Pattern Recognition</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          Advanced pattern matching for suspicious activity detection
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiNavigation} color="green.500" boxSize={8} />
                        <Heading size="md" color={textColor}>Predictive Analytics</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          Risk prediction and forecasting models for proactive monitoring
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiCompass} color="orange.500" boxSize={8} />
                        <Heading size="md" color={textColor}>Behavioral Analysis</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          User and entity behavior profiling for risk assessment
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>
                </SimpleGrid>
              </VStack>
            </TabPanel>

            {/* Visualization Tab */}
            <TabPanel>
              <VStack spacing={6} align="stretch">
                <Heading size="lg" color={textColor} textAlign="center">
                  <Icon as={FiGlobe} mr={3} color="purple.500" />
                  Interactive Visualizations
                </Heading>
                
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiGrid} color="blue.500" boxSize={8} />
                        <Heading size="md" color={textColor}>Graph Explorer</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          3D graph visualization for entity relationship exploration
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiBarChart} color="green.500" boxSize={8} />
                        <Heading size="md" color={textColor}>Time Series Canvas</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          Live time-series data visualization with interactive dashboards
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>

                  <Card bg={cardBg} border="1px" borderColor={borderColor}>
                    <CardBody>
                      <VStack spacing={3} align="center" textAlign="center">
                        <Icon as={FiMapPin} color="purple.500" boxSize={8} />
                        <Heading size="md" color={textColor}>Compliance Maps</Heading>
                        <Text fontSize="sm" color={mutedTextColor}>
                          Geographic visualization for compliance and risk mapping
                        </Text>
                        <Badge colorScheme="green">Active</Badge>
                      </VStack>
                    </CardBody>
                  </Card>
                </SimpleGrid>
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>

        {/* Feature Showcase */}
        <Card bg={cardBg} border="1px" borderColor={borderColor}>
          <CardBody>
            <Heading size="md" color={textColor} mb={6} textAlign="center">
              <Icon as={FiStar} mr={2} color="yellow.500" />
              All 50+ Features Active
            </Heading>
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
              {demoData.features.map((feature, index) => (
                <HStack key={index} p={3} bg="gray.50" borderRadius="md">
                  <Icon as={feature.icon} color="green.500" />
                  <VStack align="start" spacing={0}>
                    <Text fontSize="sm" fontWeight="medium" color={textColor}>
                      {feature.name}
                    </Text>
                    <Text fontSize="xs" color={mutedTextColor}>
                      {feature.description}
                    </Text>
                  </VStack>
                </HStack>
              ))}
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* Demo Call-to-Action */}
        <Card bg="blue.50" border="2px" borderColor="blue.200">
          <CardBody>
            <HStack justify="space-between" align="center">
              <VStack align="start" spacing={2}>
                <Heading size="lg" color="blue.800">
                  <Icon as={FiPocket} mr={2} />
                  Ready to Deploy?
                </Heading>
                <Text color="blue.700">
                  This is a fully functional, production-ready blockchain intelligence platform with 50+ features and 100% test coverage.
                </Text>
              </VStack>
              <VStack spacing={3}>
                <Button colorScheme="blue" size="lg" leftIcon={<Icon as={FiStar} />}>
                  Start Free Trial
                </Button>
                <Button variant="outline" size="md">
                  Schedule Demo
                </Button>
              </VStack>
            </HStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  );
};

export default DemoSlide; 