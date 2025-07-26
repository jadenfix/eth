import React from 'react';
import { ResponsiveLayout } from '../../src/components/organisms';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  SimpleGrid,
  Card,
  CardBody,
  Button,
  Divider,
  List,
  ListItem,
  ListIcon,
  Progress,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from '@chakra-ui/react';
import { AddIcon, CheckCircleIcon, SettingsIcon } from '@chakra-ui/icons';

const SignalBuilderPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="Signal Builder | Workflow Builder"
      description="Visual signal composition and trading algorithm builder"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">⚙️</Text>
            <Text fontSize="3xl" fontWeight="bold">
              Signal Builder
            </Text>
            <Badge colorScheme="purple" size="lg">Visual Editor</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Drag-and-drop signal composition tool for creating complex trading and analysis algorithms
          </Text>
        </Box>

        {/* Quick Actions */}
        <Card>
          <CardBody>
            <HStack justify="space-between" align="center">
              <VStack align="start" spacing={2}>
                <Text fontSize="xl" fontWeight="bold">Build Your First Signal</Text>
                <Text color="gray.600">
                  Start with a template or create from scratch
                </Text>
              </VStack>
              <HStack spacing={4}>
                <Button 
                  leftIcon={<AddIcon />} 
                  colorScheme="blue"
                  size="lg"
                >
                  New Signal
                </Button>
                <Button 
                  variant="outline"
                  size="lg"
                >
                  Browse Templates
                </Button>
              </HStack>
            </HStack>
          </CardBody>
        </Card>

        {/* Signal Components */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">📊</Text>
                  <Text fontSize="xl" fontWeight="bold">Data Sources</Text>
                </HStack>
                <Text color="gray.600" fontSize="sm">
                  Connect to blockchain data streams
                </Text>
                
                <List spacing={1} fontSize="sm">
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Block data
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    Transaction pools
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    DEX prices
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="orange.500" />
                    Gas metrics
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🔧</Text>
                  <Text fontSize="xl" fontWeight="bold">Processors</Text>
                </HStack>
                <Text color="gray.600" fontSize="sm">
                  Transform and analyze data
                </Text>
                
                <List spacing={1} fontSize="sm">
                  <ListItem>
                    <ListIcon as={SettingsIcon} color="green.500" />
                    Filters
                  </ListItem>
                  <ListItem>
                    <ListIcon as={SettingsIcon} color="blue.500" />
                    Aggregators
                  </ListItem>
                  <ListItem>
                    <ListIcon as={SettingsIcon} color="purple.500" />
                    Comparators
                  </ListItem>
                  <ListItem>
                    <ListIcon as={SettingsIcon} color="orange.500" />
                    Math functions
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🤖</Text>
                  <Text fontSize="xl" fontWeight="bold">AI Models</Text>
                </HStack>
                <Text color="gray.600" fontSize="sm">
                  Apply machine learning
                </Text>
                
                <List spacing={1} fontSize="sm">
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Anomaly detection
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    Price prediction
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    Risk scoring
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="orange.500" />
                    Classification
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🚨</Text>
                  <Text fontSize="xl" fontWeight="bold">Actions</Text>
                </HStack>
                <Text color="gray.600" fontSize="sm">
                  Execute when conditions are met
                </Text>
                
                <List spacing={1} fontSize="sm">
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Send alerts
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    Webhook calls
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    Email/Slack
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="orange.500" />
                    Data export
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Sample Templates */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Popular Signal Templates</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} w="full">
                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">🎯</Text>
                          <Text fontWeight="medium">MEV Sandwich Detection</Text>
                        </HStack>
                        <Badge colorScheme="red" size="sm">Advanced</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Detect sandwich attacks in mempool transactions
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Mempool</Badge>
                        <Badge size="xs">Pattern Match</Badge>
                        <Badge size="xs">Alert</Badge>
                      </HStack>
                      <Button size="sm" colorScheme="blue" variant="outline">
                        Use Template
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">📈</Text>
                          <Text fontWeight="medium">Large Transaction Alert</Text>
                        </HStack>
                        <Badge colorScheme="green" size="sm">Beginner</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Alert when transactions exceed value threshold
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Filter</Badge>
                        <Badge size="xs">Threshold</Badge>
                        <Badge size="xs">Notification</Badge>
                      </HStack>
                      <Button size="sm" colorScheme="blue" variant="outline">
                        Use Template
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">🔍</Text>
                          <Text fontWeight="medium">Whale Movement Tracker</Text>
                        </HStack>
                        <Badge colorScheme="purple" size="sm">Intermediate</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Track large holders' transaction patterns
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Entity ID</Badge>
                        <Badge size="xs">Balance</Badge>
                        <Badge size="xs">Analysis</Badge>
                      </HStack>
                      <Button size="sm" colorScheme="blue" variant="outline">
                        Use Template
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">⚡</Text>
                          <Text fontWeight="medium">Gas Price Optimization</Text>
                        </HStack>
                        <Badge colorScheme="orange" size="sm">Advanced</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Predict optimal gas prices using ML
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Gas Data</Badge>
                        <Badge size="xs">ML Model</Badge>
                        <Badge size="xs">Prediction</Badge>
                      </HStack>
                      <Button size="sm" colorScheme="blue" variant="outline">
                        Use Template
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Active Signals */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Your Active Signals</Text>
              <Divider />
              
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>Signal Name</Th>
                    <Th>Type</Th>
                    <Th>Status</Th>
                    <Th>Triggers</Th>
                    <Th>Last Run</Th>
                    <Th>Actions</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td>ETH Large Transfers</Td>
                    <Td>Alert</Td>
                    <Td><Badge colorScheme="green" size="sm">ACTIVE</Badge></Td>
                    <Td>47</Td>
                    <Td>2 min ago</Td>
                    <Td>
                      <Button size="xs" variant="outline">Edit</Button>
                    </Td>
                  </Tr>
                  <Tr>
                    <Td>DeFi Arbitrage Bot</Td>
                    <Td>Analysis</Td>
                    <Td><Badge colorScheme="blue" size="sm">RUNNING</Badge></Td>
                    <Td>156</Td>
                    <Td>1 min ago</Td>
                    <Td>
                      <Button size="xs" variant="outline">Edit</Button>
                    </Td>
                  </Tr>
                  <Tr>
                    <Td>Gas Price Prophet</Td>
                    <Td>ML</Td>
                    <Td><Badge colorScheme="yellow" size="sm">PAUSED</Badge></Td>
                    <Td>23</Td>
                    <Td>5 min ago</Td>
                    <Td>
                      <Button size="xs" variant="outline">Edit</Button>
                    </Td>
                  </Tr>
                </Tbody>
              </Table>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default SignalBuilderPage;
