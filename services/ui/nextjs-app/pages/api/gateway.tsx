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
  Button,
  Divider,
  List,
  ListItem,
  ListIcon,
} from '@chakra-ui/react';
import { ExternalLinkIcon, CheckCircleIcon } from '@chakra-ui/icons';

const APIGatewayPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="API Gateway | API Layer"
      description="Unified API access with gRPC, REST, and WebSocket support"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">🚪</Text>
            <Text fontSize="3xl" fontWeight="bold">
              API Gateway
            </Text>
            <Badge colorScheme="blue" size="lg">Active</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Unified API gateway providing gRPC, REST, and WebSocket access to all platform services
          </Text>
        </Box>

        {/* API Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Requests/sec</StatLabel>
                <StatNumber>2.4K</StatNumber>
                <StatHelpText>Current load</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Success Rate</StatLabel>
                <StatNumber>99.2%</StatNumber>
                <StatHelpText>24 hour average</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>P95 Latency</StatLabel>
                <StatNumber>142ms</StatNumber>
                <StatHelpText>Response time</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Active Clients</StatLabel>
                <StatNumber>847</StatNumber>
                <StatHelpText>Authenticated sessions</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* API Protocols */}
        <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6}>
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🔗</Text>
                  <Text fontSize="xl" fontWeight="bold">REST API</Text>
                </HStack>
                <Text color="gray.600">
                  Standard HTTP REST endpoints for web and mobile clients
                </Text>
                
                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    JSON request/response
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    OAuth 2.0 authentication
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    Rate limiting & throttling
                  </ListItem>
                  <ListItem>
                    <ListIcon as={ExternalLinkIcon} color="orange.500" />
                    OpenAPI 3.0 specification
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">⚡</Text>
                  <Text fontSize="xl" fontWeight="bold">gRPC API</Text>
                </HStack>
                <Text color="gray.600">
                  High-performance gRPC for service-to-service communication
                </Text>
                
                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Protocol Buffers
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    HTTP/2 multiplexing
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    Streaming support
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="orange.500" />
                    Auto-generated clients
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🔄</Text>
                  <Text fontSize="xl" fontWeight="bold">WebSocket</Text>
                </HStack>
                <Text color="gray.600">
                  Real-time bidirectional communication for live data
                </Text>
                
                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Real-time data streams
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    Live dashboard updates
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    Event subscriptions
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="orange.500" />
                    Automatic reconnection
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Available Endpoints */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Available API Endpoints</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} w="full">
                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <HStack>
                        <Badge colorScheme="blue">REST</Badge>
                        <Text fontWeight="medium">/api/v1/ethereum/*</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Ethereum blockchain data queries
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">GET</Badge>
                        <Badge size="xs">POST</Badge>
                        <Badge size="xs">WebSocket</Badge>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <HStack>
                        <Badge colorScheme="purple">GraphQL</Badge>
                        <Text fontWeight="medium">/graphql</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Flexible graph-based queries
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Query</Badge>
                        <Badge size="xs">Mutation</Badge>
                        <Badge size="xs">Subscription</Badge>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <HStack>
                        <Badge colorScheme="green">gRPC</Badge>
                        <Text fontWeight="medium">intelligence.proto</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        AI/ML model inference services
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Unary</Badge>
                        <Badge size="xs">Stream</Badge>
                        <Badge size="xs">Bidirectional</Badge>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <HStack>
                        <Badge colorScheme="orange">WebSocket</Badge>
                        <Text fontWeight="medium">/ws/live</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        Real-time data subscriptions
                      </Text>
                      <HStack spacing={2}>
                        <Badge size="xs">Blocks</Badge>
                        <Badge size="xs">Transactions</Badge>
                        <Badge size="xs">Alerts</Badge>
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Documentation & Tools */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Developer Tools</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} w="full">
                <Button 
                  leftIcon={<ExternalLinkIcon />}
                  colorScheme="blue" 
                  variant="outline"
                  size="lg"
                >
                  API Documentation
                </Button>
                
                <Button 
                  leftIcon={<ExternalLinkIcon />}
                  colorScheme="purple" 
                  variant="outline"
                  size="lg"
                >
                  GraphQL Playground
                </Button>
                
                <Button 
                  leftIcon={<ExternalLinkIcon />}
                  colorScheme="green" 
                  variant="outline"
                  size="lg"
                >
                  gRPC Proto Files
                </Button>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Technical Stack */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Technical Implementation</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Gateway Infrastructure</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Google Cloud Run deployment</ListItem>
                    <ListItem>• Cloud Load Balancer</ListItem>
                    <ListItem>• Cloud Armor DDoS protection</ListItem>
                    <ListItem>• Global CDN distribution</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Security & Monitoring</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• OAuth 2.0 / JWT authentication</ListItem>
                    <ListItem>• API key management</ListItem>
                    <ListItem>• Rate limiting & quotas</ListItem>
                    <ListItem>• Request/response logging</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="blue" size="sm" mr={4}>
                  Generate API Key
                </Button>
                <Button variant="outline" size="sm">
                  View Metrics
                </Button>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default APIGatewayPage;
