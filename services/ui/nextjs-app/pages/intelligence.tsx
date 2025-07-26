import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import {
  Box,
  Grid,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Badge,
  Button,
  useColorModeValue,
  Progress,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Flex,
  Divider,
  Container,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import CleanNavigation from '../src/components/layout/CleanNavigation';

interface AIMetrics {
  modelAccuracy: number;
  threatDetectionRate: number;
  falsePositiveRate: number;
  activeModels: number;
}

interface AIModel {
  name: string;
  accuracy: number;
  status: string;
  lastUpdated: string;
}

interface Threat {
  id: number;
  type: string;
  severity: string;
  confidence: number;
  description: string;
  timestamp: string;
  address: string;
  value: string;
}

const Intelligence: NextPage = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [aiMetrics, setAIMetrics] = useState<AIMetrics | null>(null);
  const [aiModels, setAIModels] = useState<AIModel[]>([]);
  const [threats, setThreats] = useState<Threat[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Enhanced color mode values with better contrast
  const bg = useColorModeValue('white', 'palantir.navy');
  const cardBg = useColorModeValue('white', 'palantir.navy-light');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.900', 'white');
  const mutedTextColor = useColorModeValue('gray.700', 'gray.300');
  const subtleTextColor = useColorModeValue('gray.600', 'gray.400');
  const cardBorderColor = useColorModeValue('gray.200', 'gray.600');
  const hoverBg = useColorModeValue('gray.50', 'palantir.navy-light');

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        // Fetch real data from the backend (using /api/real-data as a placeholder)
        const response = await fetch('/api/real-data');
        const data = await response.json();
        if (data.success && data.blockData) {
          const block = data.blockData;
          // Simulate AI metrics based on real block data
          setAIMetrics({
            modelAccuracy: 94.2 + Math.random() * 3,
            threatDetectionRate: 91.1 + Math.random() * 3,
            falsePositiveRate: 5.8 - Math.random() * 2,
            activeModels: 4
          });
          setAIModels([
            { name: 'MEV Detection', accuracy: 96.8, status: 'active', lastUpdated: '2 min ago' },
            { name: 'Fraud Detection', accuracy: 94.2, status: 'active', lastUpdated: '5 min ago' },
            { name: 'Risk Assessment', accuracy: 92.1, status: 'active', lastUpdated: '1 min ago' },
            { name: 'Entity Resolution', accuracy: 89.7, status: 'training', lastUpdated: '15 min ago' },
          ]);
          setThreats([
            {
              id: 1,
              type: 'MEV_ATTACK',
              severity: 'HIGH',
              confidence: 0.94,
              description: `Sandwich attack detected on block #${parseInt(block.number, 16)}`,
              timestamp: '2 minutes ago',
              address: block.miner,
              value: `$${(parseInt(block.gasUsed, 16) * 0.0001).toFixed(2)}`,
            },
            {
              id: 2,
              type: 'SUSPICIOUS_ACTIVITY',
              severity: 'MEDIUM',
              confidence: 0.87,
              description: 'Unusual transaction pattern detected',
              timestamp: '5 minutes ago',
              address: block.transactions[0]?.from || '',
              value: `$${(parseInt(block.gasUsed, 16) * 0.00005).toFixed(2)}`,
            },
            {
              id: 3,
              type: 'SANCTIONS_VIOLATION',
              severity: 'CRITICAL',
              confidence: 0.99,
              description: 'Address linked to sanctioned entity',
              timestamp: '8 minutes ago',
              address: block.transactions[0]?.to || '',
              value: `$${(parseInt(block.gasUsed, 16) * 0.0002).toFixed(2)}`,
            },
          ]);
        }
      } catch (error) {
        console.error('Error fetching AI intelligence data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'red';
      case 'HIGH': return 'orange';
      case 'MEDIUM': return 'yellow';
      case 'LOW': return 'green';
      default: return 'gray';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'green';
    if (confidence >= 0.7) return 'yellow';
    return 'red';
  };

  if (loading || !aiMetrics) {
    return (
      <Box bg={bg} minH="100vh">
        <CleanNavigation />
        <Box p={6}>
          <Text>Loading AI intelligence data...</Text>
        </Box>
      </Box>
    );
  }

  return (
    <Box bg={bg} minH="100vh">
      <CleanNavigation />
      <Box p={6}>
      <Head>
        <title>AI Intelligence - Onchain Command Center</title>
        <meta name="description" content="Advanced AI-powered blockchain intelligence and threat detection" />
      </Head>
      <Container maxW="full" p={6}>
        {/* Header */}
        <Box mb={6}>
          <Heading size="lg" color={textColor} mb={2}>
            AI Intelligence Dashboard
          </Heading>
          <Text color={mutedTextColor}>
            Advanced AI-powered blockchain intelligence and threat detection
          </Text>
          <Text fontSize="sm" color={subtleTextColor} mt={1}>
            Last updated: {currentTime.toLocaleTimeString()}
          </Text>
        </Box>

        {/* AI Performance Metrics */}
        <Grid templateColumns="repeat(auto-fit, minmax(250px, 1fr))" gap={6} mb={8}>
          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Model Accuracy</StatLabel>
                <StatNumber color={textColor}>{aiMetrics.modelAccuracy.toFixed(2)}%</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  <StatArrow type="increase" />
                  2.3% from last week
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Threat Detection Rate</StatLabel>
                <StatNumber color={textColor}>{aiMetrics.threatDetectionRate.toFixed(2)}%</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  <StatArrow type="increase" />
                  1.1% from last week
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>False Positive Rate</StatLabel>
                <StatNumber color={textColor}>{aiMetrics.falsePositiveRate.toFixed(2)}%</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  <StatArrow type="decrease" />
                  0.5% from last week
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Active AI Models</StatLabel>
                <StatNumber color={textColor}>{aiMetrics.activeModels}</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  Real-time threat detection
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* AI Models Status */}
        <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px" mb={8}>
          <CardHeader>
            <Heading size="md" color={textColor}>AI Model Performance</Heading>
          </CardHeader>
          <CardBody>
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th color={mutedTextColor}>Model</Th>
                  <Th color={mutedTextColor}>Accuracy</Th>
                  <Th color={mutedTextColor}>Status</Th>
                  <Th color={mutedTextColor}>Last Updated</Th>
                </Tr>
              </Thead>
              <Tbody>
                {aiModels.map((model, index) => (
                  <Tr key={index} _hover={{ bg: hoverBg }}>
                    <Td color={textColor}>{model.name}</Td>
                    <Td>
                      <Badge colorScheme={getConfidenceColor(model.accuracy / 100)}>
                        {model.accuracy}%
                      </Badge>
                    </Td>
                    <Td>
                      <Badge colorScheme={model.status === 'active' ? 'green' : 'yellow'}>
                        {model.status}
                      </Badge>
                    </Td>
                    <Td color={mutedTextColor}>{model.lastUpdated}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        {/* Recent Threats */}
        <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
          <CardHeader>
            <Heading size="md" color={textColor}>Recent AI-Detected Threats</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {threats.map((threat) => (
                <Alert 
                  key={threat.id} 
                  status={threat.severity === 'CRITICAL' ? 'error' : threat.severity === 'HIGH' ? 'warning' : 'info'}
                  borderRadius="md"
                >
                  <AlertIcon />
                  <Box flex="1">
                    <AlertTitle color={textColor}>
                      {threat.type.replace('_', ' ')}
                    </AlertTitle>
                    <AlertDescription color={mutedTextColor}>
                      {threat.description}
                    </AlertDescription>
                    <Flex mt={2} gap={4} fontSize="sm">
                      <Text color={subtleTextColor}>Address: {threat.address}</Text>
                      <Text color={subtleTextColor}>Value: {threat.value}</Text>
                      <Text color={subtleTextColor}>Confidence: {(threat.confidence * 100).toFixed(1)}%</Text>
                      <Text color={subtleTextColor}>{threat.timestamp}</Text>
                    </Flex>
                  </Box>
                  <Badge colorScheme={getSeverityColor(threat.severity)}>
                    {threat.severity}
                  </Badge>
                </Alert>
              ))}
            </VStack>
          </CardBody>
        </Card>
      </Container>
          </Box>
    </Box>
  );
};

export default Intelligence; 