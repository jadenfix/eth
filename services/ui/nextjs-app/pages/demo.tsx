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
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useColorModeValue,
  Icon,
  Flex,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  List,
  ListItem,
  ListIcon,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  Textarea,
  Select,
  Switch,
  FormControl,
  FormLabel,
  FormHelperText,
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
  FiPocket
} from 'react-icons/fi';

// Mock data for demo
const mockData = {
  systemHealth: {
    status: 'healthy',
    uptime: '99.9%',
    services: [
      { name: 'Ethereum Ingester', status: 'active', latency: '45ms' },
      { name: 'Graph API', status: 'active', latency: '12ms' },
      { name: 'Voice Ops', status: 'active', latency: '78ms' },
      { name: 'MEV Agent', status: 'active', latency: '23ms' },
      { name: 'Entity Resolution', status: 'active', latency: '156ms' },
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
    { id: 1, type: 'mev', severity: 'high', message: 'Front-running attack detected on Uniswap V3', time: '2 min ago' },
    { id: 2, type: 'sanctions', severity: 'medium', message: 'OFAC-sanctioned address detected in transaction', time: '5 min ago' },
    { id: 3, type: 'anomaly', severity: 'low', message: 'Unusual transaction pattern detected', time: '8 min ago' },
    { id: 4, type: 'arbitrage', severity: 'info', message: 'Cross-DEX arbitrage opportunity identified', time: '12 min ago' },
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
  ]
};

const DemoPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [isLive, setIsLive] = useState(true);
  const [selectedEntity, setSelectedEntity] = useState(null);
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
        // Simulate real-time updates
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
            <Heading size="2xl" color={textColor}>
              🎯 Onchain Command Center
            </Heading>
            <Text color={mutedTextColor} fontSize="lg">
              Enterprise Blockchain Intelligence Platform - Live Demo
            </Text>
          </VStack>
          <HStack spacing={4}>
            <Button
              leftIcon={<Icon as={isLive ? FiPause : FiPlay} />}
              colorScheme={isLive ? 'red' : 'green'}
              onClick={() => setIsLive(!isLive)}
            >
              {isLive ? 'Pause Live' : 'Start Live'}
            </Button>
            <Button
              leftIcon={<Icon as={FiRefreshCw} />}
              variant="outline"
              onClick={() => {
                toast({
                  title: "Data Refreshed",
                  description: "All metrics updated",
                  status: "success",
                  duration: 2000,
                });
              }}
            >
              Refresh
            </Button>
          </HStack>
        </HStack>

        {/* System Status Banner */}
        <Alert status="success" borderRadius="lg">
          <AlertIcon />
          <Box>
            <AlertTitle>System Status: All Services Operational</AlertTitle>
            <AlertDescription>
              25/25 E2E tests passing • 50+ features active • Production ready
            </AlertDescription>
          </Box>
        </Alert>

        {/* Main Dashboard Grid */}
        <Grid templateColumns="repeat(12, 1fr)" gap={6}>
          {/* Left Column - Key Metrics */}
          <GridItem colSpan={8}>
            <VStack spacing={6} align="stretch">
              {/* Real-time Blockchain Metrics */}
              <Card bg={cardBg} border="1px" borderColor={borderColor}>
                <CardBody>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md" color={textColor}>
                      <Icon as={FiActivity} mr={2} />
                      Real-time Blockchain Metrics
                    </Heading>
                    <Badge colorScheme="green" variant="subtle">
                      LIVE
                    </Badge>
                  </HStack>
                  <Grid templateColumns="repeat(4, 1fr)" gap={4}>
                    <Stat>
                      <StatLabel>Blocks Processed</StatLabel>
                      <StatNumber color="blue.500">{mockData.blockchainMetrics.blocksProcessed.toLocaleString()}</StatNumber>
                      <StatHelpText>Last 24 hours</StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Transactions Analyzed</StatLabel>
                      <StatNumber color="green.500">{mockData.blockchainMetrics.transactionsAnalyzed.toLocaleString()}</StatNumber>
                      <StatHelpText>Real-time processing</StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Events Extracted</StatLabel>
                      <StatNumber color="purple.500">{mockData.blockchainMetrics.eventsExtracted.toLocaleString()}</StatNumber>
                      <StatHelpText>Smart contract events</StatHelpText>
                    </Stat>
                    <Stat>
                      <StatLabel>Entities Resolved</StatLabel>
                      <StatNumber color="orange.500">{mockData.blockchainMetrics.entitiesResolved.toLocaleString()}</StatNumber>
                      <StatHelpText>AI-powered matching</StatHelpText>
                    </Stat>
                  </Grid>
                </CardBody>
              </Card>

              {/* MEV & Risk Intelligence */}
              <Card bg={cardBg} border="1px" borderColor={borderColor}>
                <CardBody>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md" color={textColor}>
                      <Icon as={FiZap} mr={2} />
                      MEV & Risk Intelligence
                    </Heading>
                    <HStack spacing={2}>
                      <Badge colorScheme="red" variant="subtle">
                        {mockData.blockchainMetrics.mevDetected} MEV Detected
                      </Badge>
                      <Badge colorScheme="orange" variant="subtle">
                        {mockData.blockchainMetrics.riskAlerts} Risk Alerts
                      </Badge>
                    </HStack>
                  </HStack>
                  <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                    {mockData.mevOpportunities.map((opp) => (
                      <Card key={opp.id} variant="outline" size="sm">
                        <CardBody p={3}>
                          <HStack justify="space-between" mb={2}>
                            <Icon as={getMevTypeIcon(opp.type)} color="blue.500" />
                            <Badge colorScheme={opp.risk === 'high' ? 'red' : opp.risk === 'medium' ? 'orange' : 'green'}>
                              {opp.risk}
                            </Badge>
                          </HStack>
                          <Text fontWeight="bold" fontSize="sm">{opp.profit}</Text>
                          <Text fontSize="xs" color={mutedTextColor} textTransform="capitalize">
                            {opp.type} opportunity
                          </Text>
                          <Badge size="sm" colorScheme={opp.status === 'active' ? 'green' : opp.status === 'monitoring' ? 'blue' : 'gray'}>
                            {opp.status}
                          </Badge>
                        </CardBody>
                      </Card>
                    ))}
                  </Grid>
                </CardBody>
              </Card>

              {/* Entity Resolution Dashboard */}
              <Card bg={cardBg} border="1px" borderColor={borderColor}>
                <CardBody>
                  <HStack justify="space-between" mb={4}>
                    <Heading size="md" color={textColor}>
                      <Icon as={FiUsers} mr={2} />
                      Entity Resolution
                    </Heading>
                    <HStack spacing={2}>
                      <Text fontSize="sm" color={mutedTextColor}>
                        Confidence Score:
                      </Text>
                      <Badge colorScheme="green" variant="subtle">
                        {mockData.entityResolution.confidenceScore}%
                      </Badge>
                    </HStack>
                  </HStack>
                  <VStack spacing={3} align="stretch">
                    {mockData.entityResolution.recentMatches.map((match, index) => (
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
            </VStack>
          </GridItem>

          {/* Right Column - Alerts & Controls */}
          <GridItem colSpan={4}>
            <VStack spacing={6} align="stretch">
              {/* System Health */}
              <Card bg={cardBg} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Heading size="md" color={textColor} mb={4}>
                    <Icon as={FiMonitor} mr={2} />
                    System Health
                  </Heading>
                  <VStack spacing={3} align="stretch">
                    {mockData.systemHealth.services.map((service, index) => (
                      <Box key={index}>
                        <HStack justify="space-between" mb={1}>
                          <Text fontSize="sm" fontWeight="medium">{service.name}</Text>
                          <Badge colorScheme="green" size="sm">{service.status}</Badge>
                        </HStack>
                        <Text fontSize="xs" color={mutedTextColor}>{service.latency} latency</Text>
                        <Progress value={100} size="xs" colorScheme="green" mt={1} />
                      </Box>
                    ))}
                  </VStack>
                </CardBody>
              </Card>

              {/* Real-time Alerts */}
              <Card bg={cardBg} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Heading size="md" color={textColor} mb={4}>
                    <Icon as={FiAlertTriangle} mr={2} />
                    Live Alerts
                  </Heading>
                  <VStack spacing={3} align="stretch" maxH="400px" overflowY="auto">
                    {mockData.realTimeAlerts.map((alert) => (
                      <Box key={alert.id} p={3} border="1px" borderColor={borderColor} borderRadius="md">
                        <HStack justify="space-between" mb={1}>
                          <Badge colorScheme={getSeverityColor(alert.severity)} size="sm">
                            {alert.type.toUpperCase()}
                          </Badge>
                          <Text fontSize="xs" color={mutedTextColor}>{alert.time}</Text>
                        </HStack>
                        <Text fontSize="sm" color={textColor}>{alert.message}</Text>
                      </Box>
                    ))}
                  </VStack>
                </CardBody>
              </Card>

              {/* Quick Actions */}
              <Card bg={cardBg} border="1px" borderColor={borderColor}>
                <CardBody>
                  <Heading size="md" color={textColor} mb={4}>
                    <Icon as={FiSettings} mr={2} />
                    Quick Actions
                  </Heading>
                  <VStack spacing={3} align="stretch">
                    <Button
                      leftIcon={<Icon as={FiSearch} />}
                      variant="outline"
                      size="sm"
                      onClick={onOpen}
                    >
                      Search Entities
                    </Button>
                    <Button
                      leftIcon={<Icon as={FiEye} />}
                      variant="outline"
                      size="sm"
                    >
                      View Analytics
                    </Button>
                    <Button
                      leftIcon={<Icon as={FiShield} />}
                      variant="outline"
                      size="sm"
                    >
                      Security Audit
                    </Button>
                    <Button
                      leftIcon={<Icon as={FiHeadphones} />}
                      variant="outline"
                      size="sm"
                    >
                      Voice Commands
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            </VStack>
          </GridItem>
        </Grid>

        {/* Feature Showcase Tabs */}
        <Card bg={cardBg} border="1px" borderColor={borderColor}>
          <CardBody>
            <Tabs onChange={setActiveTab} index={activeTab}>
              <TabList>
                <Tab><Icon as={FiDatabase} mr={2} />Data Ingestion</Tab>
                <Tab><Icon as={FiCpu} mr={2} />AI Intelligence</Tab>
                <Tab><Icon as={FiShield} mr={2} />Security & Compliance</Tab>
                                  <Tab><Icon as={FiBarChart} mr={2} />Analytics</Tab>
                <Tab><Icon as={FiGlobe} mr={2} />Visualization</Tab>
              </TabList>

              <TabPanels>
                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Heading size="md" color={textColor}>Real-time Blockchain Data Ingestion</Heading>
                    <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiActivity} color="blue.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Live Block Processing</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Real-time Ethereum blockchain data ingestion with sub-second latency
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiGitBranch} color="green.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Multi-chain Support</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Extensible architecture supporting Ethereum, Polygon, and more
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiLayers} color="purple.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Event Extraction</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Smart contract event parsing and indexing for complex analysis
                          </Text>
                        </CardBody>
                      </Card>
                    </Grid>
                  </VStack>
                </TabPanel>

                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Heading size="md" color={textColor}>AI-Powered Intelligence</Heading>
                    <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiTarget} color="red.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">MEV Detection</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Real-time detection of front-running, sandwich attacks, and arbitrage
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiUsers} color="orange.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Entity Resolution</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            AI-powered address clustering and real-world entity mapping
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiTrendingUp} color="green.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Risk Intelligence</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            ML-powered fraud detection and anomaly analysis
                          </Text>
                        </CardBody>
                      </Card>
                    </Grid>
                  </VStack>
                </TabPanel>

                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Heading size="md" color={textColor}>Enterprise Security & Compliance</Heading>
                    <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiShield} color="blue.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Access Control</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Role-based access control with fine-grained permissions
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiCheckCircle} color="green.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">OFAC Screening</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Real-time sanctions list checking and compliance monitoring
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiAward} color="purple.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">SOC2 Compliance</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Complete audit trails and security controls compliance
                          </Text>
                        </CardBody>
                      </Card>
                    </Grid>
                  </VStack>
                </TabPanel>

                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Heading size="md" color={textColor}>Advanced Analytics</Heading>
                    <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiPieChart} color="blue.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Pattern Recognition</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Advanced pattern matching for suspicious activity detection
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiNavigation} color="green.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Predictive Analytics</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Risk prediction and forecasting models for proactive monitoring
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiCompass} color="orange.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Behavioral Analysis</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            User and entity behavior profiling for risk assessment
                          </Text>
                        </CardBody>
                      </Card>
                    </Grid>
                  </VStack>
                </TabPanel>

                <TabPanel>
                  <VStack spacing={4} align="stretch">
                    <Heading size="md" color={textColor}>Interactive Visualizations</Heading>
                    <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiGrid} color="blue.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Graph Explorer</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            3D graph visualization for entity relationship exploration
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiBarChart} color="green.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Time Series Canvas</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Live time-series data visualization with interactive dashboards
                          </Text>
                        </CardBody>
                      </Card>
                      <Card variant="outline">
                        <CardBody>
                          <Icon as={FiMapPin} color="purple.500" boxSize={6} mb={2} />
                          <Text fontWeight="bold">Compliance Maps</Text>
                          <Text fontSize="sm" color={mutedTextColor}>
                            Geographic visualization for compliance and risk mapping
                          </Text>
                        </CardBody>
                      </Card>
                    </Grid>
                  </VStack>
                </TabPanel>
              </TabPanels>
            </Tabs>
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

      {/* Search Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Search Entities</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Search Type</FormLabel>
                <Select placeholder="Select search type">
                  <option value="address">Blockchain Address</option>
                  <option value="entity">Entity Name</option>
                  <option value="transaction">Transaction Hash</option>
                  <option value="contract">Smart Contract</option>
                </Select>
              </FormControl>
              <FormControl>
                <FormLabel>Search Query</FormLabel>
                <Input placeholder="Enter search term..." />
                <FormHelperText>Search across all blockchain data and resolved entities</FormHelperText>
              </FormControl>
              <Button colorScheme="blue" width="full">
                Search
              </Button>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default DemoPage; 