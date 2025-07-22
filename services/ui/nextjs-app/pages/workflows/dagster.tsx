import React from 'react';
import { ResponsiveLayout } from '../../src/components/molecules';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  SimpleGrid,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  List,
  ListItem,
  ListIcon,
  Button,
  Divider,
} from '@chakra-ui/react';
import { CheckCircleIcon, SettingsIcon, RepeatIcon } from '@chakra-ui/icons';

const DagsterWorkflowsPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="Dagster Workflows | Workflow Builder"
      description="Visual workflow and signal composition using Dagster integration"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">🔗</Text>
            <Text fontSize="3xl" fontWeight="bold">
              Dagster Workflow Pipelines
            </Text>
            <Badge colorScheme="teal" size="lg">Active</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Visual workflow orchestration and signal composition with Dagster integration for data pipeline automation
          </Text>
        </Box>

        {/* Workflow Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Active Pipelines</StatLabel>
                <StatNumber>23</StatNumber>
                <StatHelpText>Running workflows</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Success Rate</StatLabel>
                <StatNumber>98.7%</StatNumber>
                <StatHelpText>Pipeline reliability</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Jobs Executed</StatLabel>
                <StatNumber>14.2K</StatNumber>
                <StatHelpText>This month</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Avg Runtime</StatLabel>
                <StatNumber>4.2min</StatNumber>
                <StatHelpText>Per pipeline</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Active Workflows */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Active Data Pipelines</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={4} w="full">
                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">🔄</Text>
                          <Text fontWeight="medium">MEV Detection Pipeline</Text>
                        </HStack>
                        <Badge colorScheme="green" size="sm">RUNNING</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Real-time MEV opportunity detection and alerting
                      </Text>
                      <Progress value={87} colorScheme="green" size="sm" />
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>Last run: 2 min ago</Text>
                        <Text>Duration: 1.2min</Text>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">🧠</Text>
                          <Text fontWeight="medium">Entity Resolution</Text>
                        </HStack>
                        <Badge colorScheme="blue" size="sm">SCHEDULED</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        AI-powered entity matching and clustering
                      </Text>
                      <Progress value={0} colorScheme="blue" size="sm" />
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>Next run: 15 min</Text>
                        <Text>Avg: 8.4min</Text>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">📊</Text>
                          <Text fontWeight="medium">Risk Scoring</Text>
                        </HStack>
                        <Badge colorScheme="purple" size="sm">RUNNING</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Transaction risk assessment and scoring
                      </Text>
                      <Progress value={45} colorScheme="purple" size="sm" />
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>Started: 3 min ago</Text>
                        <Text>ETA: 5 min</Text>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Workflow Features */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">⚙️</Text>
                  <Text fontSize="xl" fontWeight="bold">Visual Builder</Text>
                </HStack>
                <Text color="gray.600">
                  Drag-and-drop workflow designer for complex data pipelines
                </Text>
                
                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={SettingsIcon} color="blue.500" />
                    Visual pipeline editor
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Pre-built signal components
                  </ListItem>
                  <ListItem>
                    <ListIcon as={RepeatIcon} color="purple.500" />
                    Auto-retry and error handling
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="orange.500" />
                    Real-time monitoring
                  </ListItem>
                </List>

                <Box w="full">
                  <Text fontSize="sm" mb={2}>Pipeline Health</Text>
                  <Progress value={98} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">98.7% success rate</Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🎯</Text>
                  <Text fontSize="xl" fontWeight="bold">Signal Composition</Text>
                </HStack>
                <Text color="gray.600">
                  Compose complex trading and analysis signals from basic components
                </Text>
                
                <SimpleGrid columns={2} spacing={3} w="full">
                  <VStack>
                    <Badge colorScheme="blue" size="lg">Data</Badge>
                    <Text fontSize="sm">Sources</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="purple" size="lg">Transform</Badge>
                    <Text fontSize="sm">Functions</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="green" size="lg">Analyze</Badge>
                    <Text fontSize="sm">Models</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="orange" size="lg">Alert</Badge>
                    <Text fontSize="sm">Rules</Text>
                  </VStack>
                </SimpleGrid>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Pipeline Templates */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Pipeline Templates</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} w="full">
                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <HStack>
                        <Text fontSize="lg">🚨</Text>
                        <Text fontWeight="medium">Anomaly Detection</Text>
                        <Badge colorScheme="red" size="xs">Template</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Detect unusual transaction patterns and volumes
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Ingestion</Badge>
                        <Badge size="xs">ML</Badge>
                        <Badge size="xs">Alert</Badge>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <HStack>
                        <Text fontSize="lg">📈</Text>
                        <Text fontWeight="medium">Price Impact Analysis</Text>
                        <Badge colorScheme="blue" size="xs">Template</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Analyze large transactions for price impact
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">DEX Data</Badge>
                        <Badge size="xs">Analytics</Badge>
                        <Badge size="xs">Report</Badge>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Technical Stack */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Technical Architecture</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Orchestration</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Dagster Cloud integration</ListItem>
                    <ListItem>• Kubernetes job execution</ListItem>
                    <ListItem>• Auto-scaling compute resources</ListItem>
                    <ListItem>• Failure recovery and retry logic</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Data Processing</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• BigQuery data warehouse</ListItem>
                    <ListItem>• Dataflow streaming</ListItem>
                    <ListItem>• Vertex AI ML pipelines</ListItem>
                    <ListItem>• Pub/Sub event routing</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="teal" size="sm" mr={4}>
                  Create Pipeline
                </Button>
                <Button variant="outline" size="sm">
                  View All Jobs
                </Button>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default DagsterWorkflowsPage;
