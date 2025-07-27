import React from 'react';
import { ResponsiveLayout } from '../src/components/molecules';
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
  Switch,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { CheckCircleIcon, TimeIcon, ViewIcon } from '@chakra-ui/icons';

const CanvasPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="Time Series Canvas | Onchain Command Center"
      description="High-performance time series charting with Plotly.js and D3 rendering"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">📈</Text>
            <Text fontSize="3xl" fontWeight="bold">
              Time Series Canvas
            </Text>
            <Badge colorScheme="green" size="lg">Active</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            High-performance time series charting with Canvas rendering, multi-metric overlays, and real-time data streaming
          </Text>
        </Box>

        {/* Performance Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Data Points</StatLabel>
                <StatNumber>2.4M</StatNumber>
                <StatHelpText>Per chart render</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Frame Rate</StatLabel>
                <StatNumber>60fps</StatNumber>
                <StatHelpText>Smooth animations</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Update Latency</StatLabel>
                <StatNumber>12ms</StatNumber>
                <StatHelpText>Real-time updates</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Memory Usage</StatLabel>
                <StatNumber>24MB</StatNumber>
                <StatHelpText>Optimized rendering</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Chart Controls */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Chart Configuration</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Real-time Updates</FormLabel>
                  <Switch defaultChecked colorScheme="green" />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Canvas Acceleration</FormLabel>
                  <Switch defaultChecked colorScheme="blue" />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Multi-metric Overlay</FormLabel>
                  <Switch defaultChecked colorScheme="purple" />
                </FormControl>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Feature Capabilities */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Canvas Rendering */}
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🎨</Text>
                  <Text fontSize="xl" fontWeight="bold">Canvas Rendering</Text>
                </HStack>
                <Text color="gray.600">
                  Hardware-accelerated canvas rendering for massive datasets
                </Text>
                
                <Box w="full">
                  <Text fontSize="sm" mb={2}>Rendering Performance</Text>
                  <Progress value={96} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">96% GPU utilization</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    WebGL hardware acceleration
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Level-of-detail optimization
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Smooth pan & zoom
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Memory-efficient rendering
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          {/* Real-time Streaming */}
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">⚡</Text>
                  <Text fontSize="xl" fontWeight="bold">Real-time Streaming</Text>
                </HStack>
                <Text color="gray.600">
                  Live data streaming with WebSocket integration
                </Text>

                <Box w="full">
                  <Text fontSize="sm" mb={2}>Stream Health</Text>
                  <Progress value={98} colorScheme="blue" mb={2} />
                  <Text fontSize="xs" color="gray.500">98% uptime</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={TimeIcon} color="blue.500" />
                    Sub-second latency
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    WebSocket data feeds
                  </ListItem>
                  <ListItem>
                    <ListIcon as={ViewIcon} color="purple.500" />
                    Multi-metric overlays
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Auto-scaling buffers
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Data Sources */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Active Data Feeds</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4} w="full">
                <HStack>
                  <Badge colorScheme="green">Live</Badge>
                  <Text>Block Production Rate</Text>
                </HStack>
                
                <HStack>
                  <Badge colorScheme="green">Live</Badge>
                  <Text>Gas Price Trends</Text>
                </HStack>
                
                <HStack>
                  <Badge colorScheme="green">Live</Badge>
                  <Text>Transaction Volume</Text>
                </HStack>
                
                <HStack>
                  <Badge colorScheme="green">Live</Badge>
                  <Text>MEV Activity</Text>
                </HStack>
                
                <HStack>
                  <Badge colorScheme="green">Live</Badge>
                  <Text>DeFi TVL Changes</Text>
                </HStack>
                
                <HStack>
                  <Badge colorScheme="green">Live</Badge>
                  <Text>Network Hash Rate</Text>
                </HStack>
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
                  <Text fontWeight="semibold">Rendering Engine</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Plotly.js for interactive charts</ListItem>
                    <ListItem>• D3.js for custom visualizations</ListItem>
                    <ListItem>• Canvas API for performance</ListItem>
                    <ListItem>• WebGL shaders for effects</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Data Pipeline</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• WebSocket real-time feeds</ListItem>
                    <ListItem>• BigQuery time-series data</ListItem>
                    <ListItem>• Redis caching layer</ListItem>
                    <ListItem>• Pub/Sub event streaming</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="blue" size="sm" mr={4}>
                  Open Chart Builder
                </Button>
                <Button variant="outline" size="sm">
                  Export Configuration
                </Button>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default CanvasPage;
