import React, { useState, useEffect } from 'react';
import { NextPage } from 'next';
import Head from 'next/head';
import {
  Box,
  Grid,
  GridItem,
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
  IconButton,
  Tooltip,
  Divider,
  Container,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Switch,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import CleanNavigation from '../src/components/layout/CleanNavigation';

// Mock operations data


const mockActiveOperations = [
  {
    id: 1,
    name: 'MEV Detection Pipeline',
    status: 'running',
    progress: 85,
    startTime: '2 hours ago',
    estimatedCompletion: '30 min',
    resources: ['CPU: 45%', 'Memory: 67%', 'Network: 23%'],
  },
  {
    id: 2,
    name: 'Entity Resolution Job',
    status: 'running',
    progress: 62,
    startTime: '1 hour ago',
    estimatedCompletion: '45 min',
    resources: ['CPU: 23%', 'Memory: 34%', 'Network: 12%'],
  },
  {
    id: 3,
    name: 'Risk Assessment Model',
    status: 'completed',
    progress: 100,
    startTime: '30 min ago',
    estimatedCompletion: 'Completed',
    resources: ['CPU: 0%', 'Memory: 0%', 'Network: 0%'],
  },
];

const mockSystemAlerts = [
  {
    id: 1,
    type: 'PERFORMANCE',
    severity: 'LOW',
    message: 'High memory usage detected on Graph API service',
    timestamp: '5 minutes ago',
    status: 'acknowledged',
  },
  {
    id: 2,
    type: 'SECURITY',
    severity: 'MEDIUM',
    message: 'Unusual access pattern detected',
    timestamp: '12 minutes ago',
    status: 'investigating',
  },
  {
    id: 3,
    type: 'SYSTEM',
    severity: 'INFO',
    message: 'Scheduled maintenance completed successfully',
    timestamp: '1 hour ago',
    status: 'resolved',
  },
];

const Operations: NextPage = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [autoScaling, setAutoScaling] = useState(true);
  const [alertNotifications, setAlertNotifications] = useState(true);
  
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'green';
      case 'completed': return 'blue';
      case 'failed': return 'red';
      case 'pending': return 'yellow';
      default: return 'gray';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'red';
      case 'HIGH': return 'orange';
      case 'MEDIUM': return 'yellow';
      case 'LOW': return 'green';
      case 'INFO': return 'blue';
      default: return 'gray';
    }
  };

  return (
    <Box bg={bg} minH="100vh">
      <CleanNavigation />
      
      <Box p={6}>
      <Head>
        <title>Operations Center - Onchain Command Center</title>
        <meta name="description" content="Real-time operations monitoring and control center" />
      </Head>
      
      <Container maxW="full" p={6}>
        {/* Header */}
        <Box mb={6}>
          <Heading size="lg" color={textColor} mb={2}>
            Operations Center
          </Heading>
          <Text color={mutedTextColor}>
            Real-time operations monitoring and control center
          </Text>
          <Text fontSize="sm" color={subtleTextColor} mt={1}>
            Last updated: {currentTime.toLocaleTimeString()}
          </Text>
        </Box>

        {/* Operations Metrics */}
        <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6} mb={8}>
          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Active Operations</StatLabel>
                <StatNumber color={textColor}>{mockOperationsMetrics.activeOperations}</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  Currently running
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Success Rate</StatLabel>
                <StatNumber color={textColor}>{mockOperationsMetrics.successRate}%</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  <StatArrow type="increase" />
                  0.3% from yesterday
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Avg Response Time</StatLabel>
                <StatNumber color={textColor}>{mockOperationsMetrics.averageResponseTime}s</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  <StatArrow type="decrease" />
                  0.2s from yesterday
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>System Uptime</StatLabel>
                <StatNumber color={textColor}>{mockOperationsMetrics.systemUptime}%</StatNumber>
                <StatHelpText color={subtleTextColor}>
                  Last 30 days
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Control Panel */}
        <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px" mb={8}>
          <CardHeader>
            <Heading size="md" color={textColor}>System Controls</Heading>
          </CardHeader>
          <CardBody>
            <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={6}>
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-scaling" mb="0" color={textColor}>
                  Auto Scaling
                </FormLabel>
                <Switch 
                  id="auto-scaling" 
                  isChecked={autoScaling}
                  onChange={(e) => setAutoScaling(e.target.checked)}
                  colorScheme="green"
                />
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="alert-notifications" mb="0" color={textColor}>
                  Alert Notifications
                </FormLabel>
                <Switch 
                  id="alert-notifications" 
                  isChecked={alertNotifications}
                  onChange={(e) => setAlertNotifications(e.target.checked)}
                  colorScheme="blue"
                />
              </FormControl>
            </Grid>
          </CardBody>
        </Card>

        {/* Active Operations */}
        <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px" mb={8}>
          <CardHeader>
            <Heading size="md" color={textColor}>Active Operations</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {mockActiveOperations.map((operation) => (
                <Box key={operation.id} p={4} borderWidth="1px" borderRadius="md" borderColor={borderColor}>
                  <Flex justify="space-between" align="center" mb={3}>
                    <Box>
                      <Text fontWeight="bold" color={textColor}>{operation.name}</Text>
                      <Text fontSize="sm" color={mutedTextColor}>
                        Started: {operation.startTime} | ETA: {operation.estimatedCompletion}
                      </Text>
                    </Box>
                    <Badge colorScheme={getStatusColor(operation.status)}>
                      {operation.status}
                    </Badge>
                  </Flex>
                  
                  <Progress 
                    value={operation.progress} 
                    colorScheme={operation.status === 'completed' ? 'green' : 'blue'}
                    mb={3}
                  />
                  
                  <Flex gap={4} fontSize="sm">
                    {operation.resources.map((resource, index) => (
                      <Text key={index} color={subtleTextColor}>{resource}</Text>
                    ))}
                  </Flex>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>

        {/* System Alerts */}
        <Card bg={cardBg} borderColor={cardBorderColor} borderWidth="1px">
          <CardHeader>
            <Heading size="md" color={textColor}>System Alerts</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {mockSystemAlerts.map((alert) => (
                <Alert 
                  key={alert.id} 
                  status={alert.severity === 'CRITICAL' ? 'error' : alert.severity === 'HIGH' ? 'warning' : 'info'}
                  borderRadius="md"
                >
                  <AlertIcon />
                  <Box flex="1">
                    <AlertTitle color={textColor}>
                      {alert.type} Alert
                    </AlertTitle>
                    <AlertDescription color={mutedTextColor}>
                      {alert.message}
                    </AlertDescription>
                    <Text fontSize="sm" color={subtleTextColor} mt={1}>
                      {alert.timestamp}
                    </Text>
                  </Box>
                  <VStack spacing={2}>
                    <Badge colorScheme={getSeverityColor(alert.severity)}>
                      {alert.severity}
                    </Badge>
                    <Badge colorScheme={alert.status === 'resolved' ? 'green' : 'yellow'}>
                      {alert.status}
                    </Badge>
                  </VStack>
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

export default Operations; 