import React from 'react';
import { ResponsiveLayout } from '../src/components/organisms';
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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon, TimeIcon } from '@chakra-ui/icons';

const MonitoringPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="System Monitoring | Health Service"
      description="Comprehensive system health monitoring and observability service"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">📡</Text>
            <Text fontSize="3xl" fontWeight="bold">
              System Health Monitoring
            </Text>
            <Badge colorScheme="green" size="lg">All Systems Operational</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Real-time monitoring and observability for the entire blockchain intelligence platform
          </Text>
        </Box>

        {/* System Health Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>System Uptime</StatLabel>
                <StatNumber>99.97%</StatNumber>
                <StatHelpText>Last 30 days</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Response Time</StatLabel>
                <StatNumber>127ms</StatNumber>
                <StatHelpText>P95 latency</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Active Services</StatLabel>
                <StatNumber>25</StatNumber>
                <StatHelpText>All operational</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Data Processed</StatLabel>
                <StatNumber>847TB</StatNumber>
                <StatHelpText>This month</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Service Status Overview */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Service Layer Status</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4} w="full">
                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">📥</Text>
                          <Text fontWeight="medium">Ingestion Layer</Text>
                        </HStack>
                        <Badge colorScheme="green" size="sm">HEALTHY</Badge>
                      </HStack>
                      <Progress value={100} colorScheme="green" size="sm" />
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>CPU: 23%</Text>
                        <Text>Memory: 45%</Text>
                        <Text>Disk: 67%</Text>
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
                          <Text fontWeight="medium">Intelligence Layer</Text>
                        </HStack>
                        <Badge colorScheme="green" size="sm">HEALTHY</Badge>
                      </HStack>
                      <Progress value={95} colorScheme="green" size="sm" />
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>CPU: 78%</Text>
                        <Text>Memory: 62%</Text>
                        <Text>GPU: 45%</Text>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={3}>
                      <HStack justify="space-between" w="full">
                        <HStack>
                          <Text fontSize="lg">🔗</Text>
                          <Text fontWeight="medium">API Layer</Text>
                        </HStack>
                        <Badge colorScheme="green" size="sm">HEALTHY</Badge>
                      </HStack>
                      <Progress value={98} colorScheme="green" size="sm" />
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>RPS: 2.4K</Text>
                        <Text>Errors: 0.1%</Text>
                        <Text>P99: 245ms</Text>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Infrastructure Monitoring */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">☁️</Text>
                  <Text fontSize="xl" fontWeight="bold">Cloud Infrastructure</Text>
                </HStack>
                <Text color="gray.600">
                  Google Cloud Platform service monitoring
                </Text>
                
                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    GKE Clusters: 3 active (100% healthy)
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    BigQuery: 847TB processed
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Pub/Sub: 2.4M messages/hour
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Cloud Functions: 156K invocations
                  </ListItem>
                </List>

                <Box w="full">
                  <Text fontSize="sm" mb={2}>Infrastructure Health</Text>
                  <Progress value={99} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">99.7% availability</Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🚨</Text>
                  <Text fontSize="xl" fontWeight="bold">Alert Management</Text>
                </HStack>
                <Text color="gray.600">
                  Proactive monitoring and incident response
                </Text>
                
                <SimpleGrid columns={2} spacing={3} w="full">
                  <VStack>
                    <Badge colorScheme="green" size="lg">0</Badge>
                    <Text fontSize="sm">Critical Alerts</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="yellow" size="lg">2</Badge>
                    <Text fontSize="sm">Warnings</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="blue" size="lg">14</Badge>
                    <Text fontSize="sm">Info Alerts</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="gray" size="lg">847</Badge>
                    <Text fontSize="sm">Resolved</Text>
                  </VStack>
                </SimpleGrid>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Recent Incidents */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Recent System Events</Text>
              <Divider />
              
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>Event</Th>
                    <Th>Service</Th>
                    <Th>Severity</Th>
                    <Th>Status</Th>
                    <Th>Duration</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td>High CPU utilization</Td>
                    <Td>Entity Resolution</Td>
                    <Td><Badge colorScheme="yellow" size="sm">WARNING</Badge></Td>
                    <Td><Badge colorScheme="blue" size="sm">MONITORING</Badge></Td>
                    <Td>15 min</Td>
                  </Tr>
                  <Tr>
                    <Td>Dataflow job completed</Td>
                    <Td>Ingestion Pipeline</Td>
                    <Td><Badge colorScheme="blue" size="sm">INFO</Badge></Td>
                    <Td><Badge colorScheme="green" size="sm">RESOLVED</Badge></Td>
                    <Td>8.4 min</Td>
                  </Tr>
                  <Tr>
                    <Td>Neo4j connection pool resize</Td>
                    <Td>Graph API</Td>
                    <Td><Badge colorScheme="blue" size="sm">INFO</Badge></Td>
                    <Td><Badge colorScheme="green" size="sm">RESOLVED</Badge></Td>
                    <Td>2 min</Td>
                  </Tr>
                </Tbody>
              </Table>
            </VStack>
          </CardBody>
        </Card>

        {/* Monitoring Stack */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Observability Stack</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Monitoring Tools</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Google Cloud Monitoring</ListItem>
                    <ListItem>• Grafana dashboards</ListItem>
                    <ListItem>• Prometheus metrics</ListItem>
                    <ListItem>• Custom health checks</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Alerting & Incident Response</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• PagerDuty integration</ListItem>
                    <ListItem>• Slack notifications</ListItem>
                    <ListItem>• Email alert routing</ListItem>
                    <ListItem>• Auto-scaling triggers</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="green" size="sm" mr={4}>
                  View Dashboards
                </Button>
                <Button variant="outline" size="sm">
                  Configure Alerts
                </Button>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default MonitoringPage;
