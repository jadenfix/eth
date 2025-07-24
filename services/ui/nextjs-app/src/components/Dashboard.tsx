'use client';

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Heading,
  Text,
  Badge,
  Card,
  CardBody,
  CardHeader,
  Flex,
  Spinner,
  useColorModeValue,
  VStack,
  HStack,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Alert,
  AlertIcon,
  Button,
  useToast
} from '@chakra-ui/react';
import { WarningIcon, CheckCircleIcon, InfoIcon } from '@chakra-ui/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { io, Socket } from 'socket.io-client';

interface AISignal {
  signal_id: string;
  agent_name: string;
  signal_type: string;
  confidence_score: number;
  related_addresses: string[];
  related_transactions: string[];
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  timestamp: string;
  feedback_rating?: number;
}

interface MetricData {
  timestamp: string;
  value: number;
  label: string;
}

interface SystemHealth {
  ingestion_rate: number;
  processing_latency: number;
  active_agents: number;
  signal_accuracy: number;
}

const Dashboard: React.FC = () => {
  const [signals, setSignals] = useState<AISignal[]>([]);
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);
  
  const toast = useToast();
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8081');
    
    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to real-time feed');
    });

    newSocket.on('disconnect', () => {
      setIsConnected(false);
    });

    // Listen for new AI signals
    newSocket.on('ai_signal', (signal: AISignal) => {
      setSignals(prev => [signal, ...prev.slice(0, 49)]); // Keep last 50
      
      // Show toast for high severity signals
      if (['HIGH', 'CRITICAL'].includes(signal.severity)) {
        toast({
          title: `${signal.severity} Alert`,
          description: signal.description,
          status: signal.severity === 'CRITICAL' ? 'error' : 'warning',
          duration: 5000,
          isClosable: true,
        });
      }
    });

    // Listen for metrics updates
    newSocket.on('metrics', (metricsData: MetricData[]) => {
      setMetrics(metricsData);
    });

    // Listen for system health
    newSocket.on('system_health', (health: SystemHealth) => {
      setSystemHealth(health);
    });

    setSocket(newSocket);

    // Fetch initial data
    fetchInitialData();

    return () => {
      newSocket.close();
    };
  }, [toast]);

  const fetchInitialData = async () => {
    try {
      // Fetch recent signals
      const signalsResponse = await fetch('/api/signals?limit=50');
      const signalsData = await signalsResponse.json();
      setSignals(signalsData);

      // Fetch system health
      const healthResponse = await fetch('/api/health');
      const healthData = await healthResponse.json();
      setSystemHealth(healthData);

    } catch (error) {
      console.error('Error fetching initial data:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'red';
      case 'HIGH': return 'orange';
      case 'MEDIUM': return 'yellow';
      case 'LOW': return 'green';
      default: return 'gray';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return WarningIcon;
      case 'HIGH': return WarningIcon;
      case 'MEDIUM': return InfoIcon;
      case 'LOW': return CheckCircleIcon;
      default: return InfoIcon;
    }
  };

  const handleFeedback = async (signalId: string, rating: number) => {
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signal_id: signalId, rating })
      });
      
      toast({
        title: 'Feedback submitted',
        description: 'Thank you for helping improve our models',
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <Box bg={bgColor} minH="100vh" p={4}>
      <Container maxW="container.xl">
        {/* Header */}
        <Flex justify="space-between" align="center" mb={6}>
          <VStack align="start" spacing={1}>
            <Heading size="lg" color="blue.600">
              Onchain Command Center
            </Heading>
            <Text fontSize="sm" color="gray.500">
              Real-time blockchain intelligence platform
            </Text>
          </VStack>
          
          <HStack spacing={3}>
            <Badge 
              colorScheme={isConnected ? 'green' : 'red'}
              variant="solid"
              fontSize="xs"
            >
              {isConnected ? 'Live' : 'Disconnected'}
            </Badge>
            {systemHealth && (
              <Text fontSize="sm" color="gray.500">
                {systemHealth.ingestion_rate}/s events
              </Text>
            )}
          </HStack>
        </Flex>

        {/* System Health Dashboard */}
        {systemHealth && (
          <Grid templateColumns="repeat(4, 1fr)" gap={4} mb={6}>
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>Ingestion Rate</StatLabel>
                  <StatNumber>{systemHealth.ingestion_rate}/s</StatNumber>
                  <StatHelpText>Blockchain events</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
            
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>Processing Latency</StatLabel>
                  <StatNumber>{systemHealth.processing_latency}ms</StatNumber>
                  <StatHelpText>Average response time</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
            
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>Active Agents</StatLabel>
                  <StatNumber>{systemHealth.active_agents}</StatNumber>
                  <StatHelpText>AI monitoring agents</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
            
            <Card bg={cardBg}>
              <CardBody>
                <Stat>
                  <StatLabel>Signal Accuracy</StatLabel>
                  <StatNumber>{(systemHealth.signal_accuracy * 100).toFixed(1)}%</StatNumber>
                  <StatHelpText>Model performance</StatHelpText>
                </Stat>
                <Progress 
                  value={systemHealth.signal_accuracy * 100} 
                  colorScheme="blue" 
                  size="sm" 
                  mt={2}
                />
              </CardBody>
            </Card>
          </Grid>
        )}

        {/* Charts */}
        <Grid templateColumns="repeat(2, 1fr)" gap={6} mb={6}>
          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">Signal Volume</Heading>
            </CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="value" stroke="#3182CE" fill="#3182CE" fillOpacity={0.2} />
                </AreaChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>

          <Card bg={cardBg}>
            <CardHeader>
              <Heading size="md">Risk Trends</Heading>
            </CardHeader>
            <CardBody>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={metrics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#E53E3E" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
        </Grid>

        {/* AI Signals Feed */}
        <Card bg={cardBg}>
          <CardHeader>
            <Flex justify="space-between" align="center">
              <Heading size="md">AI Signals Feed</Heading>
              <Text fontSize="sm" color="gray.500">
                {signals.length} recent signals
              </Text>
            </Flex>
          </CardHeader>
          <CardBody>
            {signals.length === 0 ? (
              <Flex justify="center" align="center" h={200}>
                <VStack spacing={4}>
                  <Spinner size="lg" color="blue.500" />
                  <Text color="gray.500">Waiting for AI signals...</Text>
                </VStack>
              </Flex>
            ) : (
              <VStack spacing={3} align="stretch" maxH={600} overflowY="auto">
                {signals.map((signal) => (
                  <Alert key={signal.signal_id} status="info" variant="left-accent">
                    <AlertIcon as={getSeverityIcon(signal.severity)} />
                    <Box flex="1">
                      <Flex justify="space-between" align="start" mb={2}>
                        <VStack align="start" spacing={1} flex="1">
                          <HStack spacing={2}>
                            <Badge colorScheme={getSeverityColor(signal.severity)} size="sm">
                              {signal.severity}
                            </Badge>
                            <Badge variant="outline" size="sm">
                              {signal.agent_name}
                            </Badge>
                            <Badge variant="outline" size="sm">
                              {signal.signal_type}
                            </Badge>
                            <Text fontSize="xs" color="gray.500">
                              {new Date(signal.timestamp).toLocaleTimeString()}
                            </Text>
                          </HStack>
                          <Text fontSize="sm" fontWeight="medium">
                            {signal.description}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            Confidence: {(signal.confidence_score * 100).toFixed(1)}%
                          </Text>
                        </VStack>
                        
                        <VStack spacing={1} ml={4}>
                          <Text fontSize="xs" color="gray.500">Feedback</Text>
                          <HStack spacing={1}>
                            <Button 
                              size="xs" 
                              colorScheme="green" 
                              variant="outline"
                              onClick={() => handleFeedback(signal.signal_id, 1)}
                            >
                              ✓
                            </Button>
                            <Button 
                              size="xs" 
                              colorScheme="red" 
                              variant="outline"
                              onClick={() => handleFeedback(signal.signal_id, -1)}
                            >
                              ✗
                            </Button>
                          </HStack>
                        </VStack>
                      </Flex>
                    </Box>
                  </Alert>
                ))}
              </VStack>
            )}
          </CardBody>
        </Card>
      </Container>
    </Box>
  );
};

export default Dashboard;
