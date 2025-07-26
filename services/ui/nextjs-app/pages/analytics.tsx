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
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Divider,
  Flex,
  SimpleGrid,
} from '@chakra-ui/react';
import PalantirLayout from '../src/components/layout/PalantirLayout';

// Mock analytics data
const mockAnalyticsData = {
  totalTransactions: 1247503,
  uniqueAddresses: 89234,
  averageTransactionValue: 0.85,
  totalVolume: 2345000,
  riskScore: 23,
  anomalyDetected: 156,
  complianceScore: 94.2,
};

const mockRiskMetrics = [
  {
    category: 'High Risk Addresses',
    count: 234,
    percentage: 0.26,
    trend: 'increase',
    change: 12.5,
  },
  {
    category: 'Suspicious Transactions',
    count: 1567,
    percentage: 0.13,
    trend: 'decrease',
    change: 8.3,
  },
  {
    category: 'MEV Attacks',
    count: 89,
    percentage: 0.007,
    trend: 'increase',
    change: 23.1,
  },
  {
    category: 'Sanctions Violations',
    count: 12,
    percentage: 0.001,
    trend: 'decrease',
    change: 45.2,
  },
];

const mockTopAddresses = [
  {
    address: '0x742d35Cc6634C0532925a3b8D6Ac492395d8',
    type: 'Whale',
    balance: 1250.5,
    riskScore: 85,
    transactions: 1247,
    lastActivity: '2 minutes ago',
  },
  {
    address: '0x8ba1f109551bD432803012645Hac136c82',
    type: 'MEV Bot',
    balance: 89.2,
    riskScore: 92,
    transactions: 3456,
    lastActivity: '5 minutes ago',
  },
  {
    address: '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
    type: 'Contract',
    balance: 0,
    riskScore: 15,
    transactions: 125000,
    lastActivity: '1 hour ago',
  },
  {
    address: '0xabc123def456789ghi0123456789jklmnop',
    type: 'Exchange',
    balance: 567.8,
    riskScore: 45,
    transactions: 892,
    lastActivity: '30 minutes ago',
  },
];

const AnalyticsPage: NextPage = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('24H');
  const [selectedMetric, setSelectedMetric] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const bg = useColorModeValue('white', 'dark.800');
  const borderColor = useColorModeValue('gray.200', 'dark.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.400');

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'error';
    if (score >= 60) return 'warning';
    if (score >= 40) return 'info';
    return 'success';
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Whale': return 'crypto';
      case 'MEV Bot': return 'error';
      case 'Contract': return 'info';
      case 'Exchange': return 'warning';
      default: return 'gray';
    }
  };

  return (
    <PalantirLayout>
      <Head>
        <title>Risk Analytics - Onchain Command Center</title>
      </Head>

      <VStack spacing={6} align="stretch">
        {/* Header Section */}
        <Box>
          <HStack justify="space-between" align="center">
            <VStack align="start" spacing={1}>
              <Heading size="lg" color={textColor}>
                Risk Analytics Dashboard
              </Heading>
              <Text color={mutedTextColor} fontSize="sm">
                Comprehensive risk assessment and threat intelligence
              </Text>
            </VStack>
            <HStack spacing={4}>
              <Badge colorScheme="success" size="lg">
                LOW RISK
              </Badge>
            </HStack>
          </HStack>
        </Box>

        {/* Key Metrics Grid */}
        <Grid templateColumns="repeat(auto-fit, minmax(200px, 1fr))" gap={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Overall Risk Score</StatLabel>
                <StatNumber color={getRiskColor(mockAnalyticsData.riskScore) + '.500'}>
                  {mockAnalyticsData.riskScore}/100
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="decrease" />
                  5.2% from last 24h
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Anomalies Detected</StatLabel>
                <StatNumber color="warning.500">
                  {mockAnalyticsData.anomalyDetected}
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  12.3% from last 24h
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Compliance Score</StatLabel>
                <StatNumber color="success.500">
                  {mockAnalyticsData.complianceScore}%
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  1.8% from last 24h
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel color={mutedTextColor}>Total Volume</StatLabel>
                <StatNumber color={textColor}>
                  ${(mockAnalyticsData.totalVolume / 1000000).toFixed(1)}M
                </StatNumber>
                <StatHelpText>
                  <StatArrow type="increase" />
                  8.7% from last 24h
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
                  Timeframe
                </Text>
                <Select
                  value={selectedTimeframe}
                  onChange={(e) => setSelectedTimeframe(e.target.value)}
                  size="sm"
                  w="150px"
                >
                  <option value="1H">Last Hour</option>
                  <option value="24H">Last 24 Hours</option>
                  <option value="7D">Last 7 Days</option>
                  <option value="30D">Last 30 Days</option>
                </Select>
              </VStack>

              <VStack align="start" spacing={2}>
                <Text fontSize="sm" color={mutedTextColor} fontWeight="medium">
                  Risk Category
                </Text>
                <Select
                  value={selectedMetric}
                  onChange={(e) => setSelectedMetric(e.target.value)}
                  size="sm"
                  w="200px"
                >
                  <option value="ALL">All Categories</option>
                  <option value="HIGH_RISK">High Risk Addresses</option>
                  <option value="SUSPICIOUS">Suspicious Transactions</option>
                  <option value="MEV">MEV Attacks</option>
                  <option value="SANCTIONS">Sanctions Violations</option>
                </Select>
              </VStack>

              <VStack align="start" spacing={2} flex={1}>
                <Text fontSize="sm" color={mutedTextColor} fontWeight="medium">
                  Search Addresses
                </Text>
                <InputGroup size="sm">
                  <InputLeftElement>
                    <Text fontSize="sm" color="gray.400">⌕</Text>
                  </InputLeftElement>
                  <Input
                    placeholder="Search by address or type..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </InputGroup>
              </VStack>

              <Button colorScheme="crypto" size="sm">
                Generate Report
              </Button>
            </HStack>
          </CardBody>
        </Card>

        {/* Risk Metrics */}
        <Card>
          <CardHeader>
            <Heading size="md" color={textColor}>
              Risk Metrics Breakdown
            </Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
              {mockRiskMetrics.map((metric) => (
                <Box key={metric.category} p={4} border="1px solid" borderColor={borderColor} borderRadius="md">
                  <VStack align="stretch" spacing={3}>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color={textColor} fontWeight="medium">
                        {metric.category}
                      </Text>
                      <Badge colorScheme={metric.trend === 'increase' ? 'error' : 'success'} size="sm">
                        {metric.trend === 'increase' ? '+' : '-'}{metric.change}%
                      </Badge>
                    </HStack>
                    
                    <Stat>
                      <StatNumber fontSize="2xl" color={textColor}>
                        {metric.count.toLocaleString()}
                      </StatNumber>
                      <StatHelpText color={mutedTextColor}>
                        {metric.percentage}% of total
                      </StatHelpText>
                    </Stat>

                    <Progress
                      value={metric.percentage * 100}
                      colorScheme={metric.trend === 'increase' ? 'error' : 'success'}
                      size="sm"
                      borderRadius="full"
                    />
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* Top Risk Addresses */}
        <Card>
          <CardHeader>
            <Heading size="md" color={textColor}>
              High-Risk Addresses
            </Heading>
          </CardHeader>
          <CardBody>
            <Table variant="simple" size="sm">
              <Thead>
                <Tr>
                  <Th color={mutedTextColor}>Address</Th>
                  <Th color={mutedTextColor}>Type</Th>
                  <Th color={mutedTextColor}>Balance (ETH)</Th>
                  <Th color={mutedTextColor}>Risk Score</Th>
                  <Th color={mutedTextColor}>Transactions</Th>
                  <Th color={mutedTextColor}>Last Activity</Th>
                  <Th color={mutedTextColor}>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {mockTopAddresses.map((address) => (
                  <Tr key={address.address}>
                    <Td>
                      <Text fontSize="sm" color="crypto.400" fontFamily="mono">
                        {address.address.slice(0, 8)}...{address.address.slice(-6)}
                      </Text>
                    </Td>
                    <Td>
                      <Badge colorScheme={getTypeColor(address.type)} size="sm">
                        {address.type}
                      </Badge>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor} fontWeight="medium">
                        {address.balance.toLocaleString()}
                      </Text>
                    </Td>
                    <Td>
                      <Badge colorScheme={getRiskColor(address.riskScore)} size="sm">
                        {address.riskScore}
                      </Badge>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={textColor}>
                        {address.transactions.toLocaleString()}
                      </Text>
                    </Td>
                    <Td>
                      <Text fontSize="sm" color={mutedTextColor}>
                        {address.lastActivity}
                      </Text>
                    </Td>
                    <Td>
                      <HStack spacing={2}>
                        <Button size="xs" variant="outline">
                          Monitor
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

        {/* Risk Analysis Charts */}
        <Grid templateColumns="1fr 1fr" gap={6}>
          <Card>
            <CardHeader>
              <Heading size="md" color={textColor}>
                Risk Distribution
              </Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4} align="stretch">
                {[
                  { label: 'Low Risk (0-30)', percentage: 65, color: 'success.500' },
                  { label: 'Medium Risk (31-60)', percentage: 25, color: 'warning.500' },
                  { label: 'High Risk (61-80)', percentage: 8, color: 'error.500' },
                  { label: 'Critical Risk (81-100)', percentage: 2, color: 'error.600' },
                ].map((item) => (
                  <Box key={item.label}>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" color={textColor}>
                        {item.label}
                      </Text>
                      <Text fontSize="sm" color={mutedTextColor}>
                        {item.percentage}%
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
                Threat Intelligence
              </Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={6} align="stretch">
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" color={mutedTextColor}>
                      Known Threats
                    </Text>
                    <Text fontSize="sm" color="error.500" fontWeight="medium">
                      47 detected
                    </Text>
                  </HStack>
                  <Progress value={47} colorScheme="error" size="lg" borderRadius="full" />
                </Box>

                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" color={mutedTextColor}>
                      Suspicious Patterns
                    </Text>
                    <Text fontSize="sm" color="warning.500" fontWeight="medium">
                      156 identified
                    </Text>
                  </HStack>
                  <Progress value={156} colorScheme="warning" size="lg" borderRadius="full" />
                </Box>

                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontSize="sm" color={mutedTextColor}>
                      Sanctions Compliance
                    </Text>
                    <Text fontSize="sm" color="success.500" fontWeight="medium">
                      99.8% compliant
                    </Text>
                  </HStack>
                  <Progress value={99.8} colorScheme="success" size="lg" borderRadius="full" />
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </Grid>
      </VStack>
    </PalantirLayout>
  );
};

export default AnalyticsPage;
