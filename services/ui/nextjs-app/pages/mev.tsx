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
  Badge,
  Button,
  useColorModeValue,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Flex,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Divider,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import PalantirLayout from '../src/components/layout/PalantirLayout';

// Mock MEV data
const mockMEVData = {
  totalDetected: 156,
  totalValue: 2345000,
  averageValue: 15032,
  successRate: 87.3,
  recentDetections: 12,
};

const mockMEVEvents = [
  {
    id: 1,
    type: 'SANDWICH_ATTACK',
    description: 'Sandwich attack on Uniswap V3 ETH/USDC pair',
    victim: '0x742d35Cc6634C0532925a3b8D6Ac492395d8',
    attacker: '0x8ba1f109551bD432803012645Hac136c82',
    value: 45230,
    gasUsed: 450000,
    gasPrice: 200,
    timestamp: '2 minutes ago',
    status: 'DETECTED',
    severity: 'HIGH',
  },
  {
    id: 2,
    type: 'FRONT_RUNNING',
    description: 'Front-running large DEX trade',
    victim: '0xabc123def456789ghi0123456789jklmnop',
    attacker: '0xmev_bot_123456789abcdef0123456789',
    value: 125000,
    gasUsed: 320000,
    gasPrice: 180,
    timestamp: '5 minutes ago',
    status: 'DETECTED',
    severity: 'HIGH',
  },
  {
    id: 3,
    type: 'ARBITRAGE',
    description: 'Cross-DEX arbitrage opportunity',
    victim: '0xdef456abc789ghi0123456789jklmnopqr',
    attacker: '0xarb_bot_456789abcdef0123456789ghijk',
    value: 89000,
    gasUsed: 280000,
    gasPrice: 150,
    timestamp: '8 minutes ago',
    status: 'DETECTED',
    severity: 'MEDIUM',
  },
  {
    id: 4,
    type: 'LIQUIDATION',
    description: 'Compound protocol liquidation',
    victim: '0xghi789def012abc3456789jklmnopqrstu',
    attacker: '0xliq_bot_789abcdef0123456789ghijklmn',
    value: 67000,
    gasUsed: 220000,
    gasPrice: 120,
    timestamp: '12 minutes ago',
    status: 'DETECTED',
    severity: 'MEDIUM',
  },
];

const MEVPage: NextPage = () => {
  const [selectedType, setSelectedType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [timeRange, setTimeRange] = useState('24H');

  const bg = useColorModeValue('white', 'dark.800');
  const borderColor = useColorModeValue('gray.200', 'dark.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'HIGH': return 'error';
      case 'MEDIUM': return 'warning';
      case 'LOW': return 'info';
      default: return 'gray';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'SANDWICH_ATTACK': return 'error';
      case 'FRONT_RUNNING': return 'warning';
      case 'ARBITRAGE': return 'info';
      case 'LIQUIDATION': return 'crypto';
      default: return 'gray';
    }
  };

  const filteredEvents = mockMEVEvents.filter(event => {
    const matchesType = selectedType === 'ALL' || event.type === selectedType;
    const matchesSearch = event.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         event.victim.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         event.attacker.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <PalantirLayout>
      <Head>
        <title>MEV Detection - Onchain Command Center</title>
      </Head>

      <VStack spacing={6} align="stretch">
        {/* Header Section */}
        <Box>
          <HStack justify="space-between" align="center">
            <VStack align="start" spacing={1}>
              <Heading size="lg" color={textColor}>
                MEV Detection System
              </Heading>
              <Text color={mutedTextColor} fontSize="sm">
                Real-time detection and analysis of Maximal Extractable Value attacks
              </Text>
            </VStack>
            <HStack spacing={4}>
              <Badge colorScheme="error" size="lg">
                ACTIVE MONITORING
              </Badge>
            </HStack>
          </HStack>
        </Box>

        {/* Alert Banner */}
        <Alert status="warning" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>High MEV Activity Detected</AlertTitle>
            <AlertDescription>
              12 MEV attacks detected in the last hour. System is actively monitoring for new threats.
            </AlertDescription>
          </Box>
        </Alert>

        {/* Key Metrics Grid */}
        <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Total Detected</StatLabel>
                <StatNumber color="error.500">
                  {mockMEVData.totalDetected}
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  23% from last 24h
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Total Value</StatLabel>
                <StatNumber color={textColor}>
                  ${(mockMEVData.totalValue / 1000000).toFixed(1)}M
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  15.2% from last 24h
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Average Value</StatLabel>
                <StatNumber color={textColor}>
                  ${mockMEVData.averageValue.toLocaleString()}
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="decrease" />
                  8.7% from last 24h
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Detection Rate</StatLabel>
                <StatNumber color="success.500">
                  {mockMEVData.successRate}%
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  2.1% from last 24h
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Filters and Controls */}
        <Card>
          <CardBody>
            <HStack spacing={6} align="center">
              <VStack align="start" spacing={2}>
                <Text fontSize="sm" color={mutedTextColor} fontWeight="medium">
                  MEV Type
                </Text>
                <Select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  size="sm"
                  w="200px"
                >
                  <option value="ALL">All Types</option>
                  <option value="SANDWICH_ATTACK">Sandwich Attack</option>
                  <option value="FRONT_RUNNING">Front Running</option>
                  <option value="ARBITRAGE">Arbitrage</option>
                  <option value="LIQUIDATION">Liquidation</option>
                </Select>
              </VStack>

              <VStack align="start" spacing={2}>
                <Text fontSize="sm" color={mutedTextColor} fontWeight="medium">
                  Time Range
                </Text>
                <Select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  size="sm"
                  w="150px"
                >
                  <option value="1H">Last Hour</option>
                  <option value="24H">Last 24 Hours</option>
                  <option value="7D">Last 7 Days</option>
                  <option value="30D">Last 30 Days</option>
                </Select>
              </VStack>

              <VStack align="start" spacing={2} flex={1}>
                <Text fontSize="sm" color={mutedTextColor} fontWeight="medium">
                  Search
                </Text>
                <InputGroup size="sm">
                  <InputLeftElement>
                    <Text fontSize="sm" color="gray.400">⌕</Text>
                  </InputLeftElement>
                  <Input
                    placeholder="Search by description, victim, or attacker..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </InputGroup>
              </VStack>

              <Button colorScheme="crypto" size="sm">
                Export Data
              </Button>
            </HStack>
          </CardBody>
        </Card>

        {/* MEV Events Table */}
        <Card>
          <CardHeader>
            <HStack justify="space-between">
              <Heading size="md" color={textColor}>
                Recent MEV Events
              </Heading>
              <Text fontSize="sm" color={mutedTextColor}>
                Showing {filteredEvents.length} of {mockMEVEvents.length} events
              </Text>
            </HStack>
          </CardHeader>
          <CardBody>
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th color={mutedTextColor}>Type</Th>
                  <Th color={mutedTextColor}>Description</Th>
                  <Th color={mutedTextColor}>Victim</Th>
                  <Th color={mutedTextColor}>Attacker</Th>
                  <Th color={mutedTextColor}>Value</Th>
                  <Th color={mutedTextColor}>Gas</Th>
                  <Th color={mutedTextColor}>Severity</Th>
                  <Th color={mutedTextColor}>Time</Th>
                  <Th color={mutedTextColor}>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredEvents.map((event) => (
                  <Tr key={event.id}>
                    <Td>
                      <Badge colorScheme={getTypeColor(event.type)} size="sm">
                        {event.type.replace('_', ' ')}
                      </Badge>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor} maxW="200px" noOfLines={2}>
                        {event.description}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color="crypto.400" fontFamily="mono" maxW="120px" noOfLines={1}>
                        {event.victim.slice(0, 8)}...{event.victim.slice(-6)}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color="error.400" fontFamily="mono" maxW="120px" noOfLines={1}>
                        {event.attacker.slice(0, 8)}...{event.attacker.slice(-6)}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor} fontWeight="medium">
                        ${event.value.toLocaleString()}
                      </Text>
                    </Td>
                    <Td>
                      <VStack align="start" spacing={1}>
                        <Text fontSize="xs" color={mutedTextColor}>
                          {event.gasUsed.toLocaleString()}
                        </Text>
                        <Text fontSize="xs" color={mutedTextColor}>
                          {event.gasPrice} gwei
                        </Text>
                      </VStack>
                    </Td>
                    <Td>
                      <Badge colorScheme={getSeverityColor(event.severity)} size="sm">
                        {event.severity}
                      </Badge>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={mutedTextColor}>
                        {event.timestamp}
                      </Text>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <Button size="xs" variant="outline">
                          Details
                        </Button>
                        <Button size="xs" variant="outline" colorScheme="error">
                          Block
                        </Button>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </CardBody>
        </Card>

        {/* MEV Analysis Charts */}
        <Grid templateColumns="1fr 1fr" gap={6}>
          <Card>
            <CardHeader>
              <Heading size="md" color={textColor}>
                MEV Type Distribution
              </Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                {[
                  { type: 'Sandwich Attack', count: 45, percentage: 28.8, color: 'error.500' },
                  { type: 'Front Running', count: 38, percentage: 24.4, color: 'warning.500' },
                  { type: 'Arbitrage', count: 42, percentage: 26.9, color: 'info.500' },
                  { type: 'Liquidation', count: 31, percentage: 19.9, color: 'crypto.500' },
                ].map((item) => (
                  <Box key={item.type}>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" color={textColor}>
                        {item.type}
                      </Text>
                      <Text fontSize="sm" color={mutedTextColor}>
                        {item.count} ({item.percentage}%)
                      </Text>
                    </HStack>
                    <Progress
                      value={item.percentage}
                      colorScheme={item.color.split('.')[0] as any}
                      size="sm"
                      borderRadius="full"
                    />
                  </Box>
                ))}
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <Heading size="md" color={textColor}>
                Detection Performance
              </Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" color={mutedTextColor}>
                      Detection Accuracy
                    </Text>
                    <Text fontSize="sm" color="success.500" fontWeight="medium">
                      94.2%
                    </Text>
                  </HStack>
                  <Progress value={94.2} colorScheme="success" size="lg" borderRadius="full" />
                </Box>

                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" color={mutedTextColor}>
                      False Positive Rate
                    </Text>
                    <Text fontSize="sm" color="warning.500" fontWeight="medium">
                      5.8%
                    </Text>
                  </HStack>
                  <Progress value={5.8} colorScheme="warning" size="lg" borderRadius="full" />
                </Box>

                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" color={mutedTextColor}>
                      Response Time
                    </Text>
                    <Text fontSize="sm" color="crypto.500" fontWeight="medium">
                      2.3s avg
                    </Text>
                  </HStack>
                  <Progress value={85} colorScheme="crypto" size="lg" borderRadius="full" />
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </Grid>
      </VStack>
    </PalantirLayout>
  );
};

export default MEVPage;
