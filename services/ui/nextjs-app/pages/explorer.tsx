import React, { useState, useEffect } from 'react';
import { ResponsiveLayout } from '../src/components/organisms';
import PalantirNetworkGraph from '../src/components/molecules/PalantirNetworkGraph';
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
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { CheckCircleIcon, SearchIcon, ViewIcon, TimeIcon } from '@chakra-ui/icons';

const ExplorerPage: React.FC = () => {
  const [isLiveMode, setIsLiveMode] = useState(false);
  const [selectedEntity, setSelectedEntity] = useState<any>(null);

  return (
    <ResponsiveLayout
      title="Entity Explorer | Onchain Command Center"
      description="Interactive entity relationship explorer with network graphs and search"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">�️</Text>
            <Text fontSize="3xl" fontWeight="bold">
              Entity Explorer
            </Text>
            <Badge colorScheme="green" size="lg">Palantir-style</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Real-time blockchain entity relationship explorer with force-directed network graphs and live data streaming
          </Text>
        </Box>

        {/* Main Graph Visualization */}
        <Box height="600px" bg="gray.900" borderRadius="lg" border="1px solid" borderColor="gray.600">
          <PalantirNetworkGraph
            height={600}
            enablePhysics={true}
            showLabels={true}
            onNodeClick={(node) => setSelectedEntity(node)}
          />
        </Box>

        {/* Control Panel & Analytics */}
        <Tabs variant="enclosed" colorScheme="blue">
          <TabList>
            <Tab>🎛️ Controls</Tab>
            <Tab>📊 Analytics</Tab>
            <Tab>🚨 Risk Alerts</Tab>
            <Tab>📋 Entity Details</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Total Entities</StatLabel>
                <StatNumber>847K</StatNumber>
                <StatHelpText>Indexed addresses</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Relationships</StatLabel>
                <StatNumber>2.1M</StatNumber>
                <StatHelpText>Active connections</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Search Speed</StatLabel>
                <StatNumber>45ms</StatNumber>
                <StatHelpText>Average query time</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Graph Depth</StatLabel>
                <StatNumber>6 Hops</StatNumber>
                <StatHelpText>Maximum traversal</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Explorer Controls */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Explorer Configuration</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Real-time Updates</FormLabel>
                  <Switch defaultChecked colorScheme="green" />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Force-directed Layout</FormLabel>
                  <Switch defaultChecked colorScheme="blue" />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Auto-clustering</FormLabel>
                  <Switch defaultChecked colorScheme="purple" />
                </FormControl>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Feature Capabilities */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Network Graph */}
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🌐</Text>
                  <Text fontSize="xl" fontWeight="bold">Network Visualization</Text>
                </HStack>
                <Text color="gray.600">
                  Interactive force-directed network graphs with WebGL acceleration
                </Text>
                
                <Box w="full">
                  <Text fontSize="sm" mb={2}>Rendering Performance</Text>
                  <Progress value={94} colorScheme="blue" mb={2} />
                  <Text fontSize="xs" color="gray.500">94% GPU utilization</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={ViewIcon} color="blue.500" />
                    Force-directed layouts
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    WebGL rendering
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Interactive navigation
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Real-time clustering
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          {/* Search & Discovery */}
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🔍</Text>
                  <Text fontSize="xl" fontWeight="bold">Smart Search</Text>
                </HStack>
                <Text color="gray.600">
                  AI-powered entity search with semantic matching
                </Text>

                <Box w="full">
                  <Text fontSize="sm" mb={2}>Search Accuracy</Text>
                  <Progress value={96} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">96% relevance score</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={SearchIcon} color="purple.500" />
                    Semantic search
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Fuzzy matching
                  </ListItem>
                  <ListItem>
                    <ListIcon as={ViewIcon} color="blue.500" />
                    Entity suggestions
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Pattern detection
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Search Categories */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Entity Types</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 2, md: 3, lg: 6 }} spacing={4} w="full">
                <VStack spacing={2}>
                  <Badge colorScheme="blue" size="lg">EOA</Badge>
                  <Text fontSize="sm">Externally Owned</Text>
                  <Text fontSize="xs" color="gray.500">647K entities</Text>
                </VStack>
                
                <VStack spacing={2}>
                  <Badge colorScheme="purple" size="lg">Contract</Badge>
                  <Text fontSize="sm">Smart Contracts</Text>
                  <Text fontSize="xs" color="gray.500">156K entities</Text>
                </VStack>
                
                <VStack spacing={2}>
                  <Badge colorScheme="orange" size="lg">DEX</Badge>
                  <Text fontSize="sm">DEX Pools</Text>
                  <Text fontSize="xs" color="gray.500">23K entities</Text>
                </VStack>
                
                <VStack spacing={2}>
                  <Badge colorScheme="green" size="lg">Token</Badge>
                  <Text fontSize="sm">Token Contracts</Text>
                  <Text fontSize="xs" color="gray.500">18K entities</Text>
                </VStack>
                
                <VStack spacing={2}>
                  <Badge colorScheme="red" size="lg">Bridge</Badge>
                  <Text fontSize="sm">Cross-chain</Text>
                  <Text fontSize="xs" color="gray.500">1.2K entities</Text>
                </VStack>
                
                <VStack spacing={2}>
                  <Badge colorScheme="teal" size="lg">CEX</Badge>
                  <Text fontSize="sm">Exchanges</Text>
                  <Text fontSize="xs" color="gray.500">341 entities</Text>
                </VStack>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Technical Architecture */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Technical Stack</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Graph Engine</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Neo4j graph database</ListItem>
                    <ListItem>• Cypher query optimization</ListItem>
                    <ListItem>• Bloom graph visualization</ListItem>
                    <ListItem>• Real-time graph updates</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Search Infrastructure</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Elasticsearch indexing</ListItem>
                    <ListItem>• Vector similarity search</ListItem>
                    <ListItem>• Autocomplete suggestions</ListItem>
                    <ListItem>• Faceted search filters</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="blue" size="sm" mr={4}>
                  Launch Explorer
                </Button>
                <Button variant="outline" size="sm">
                  API Documentation
                </Button>
              </Box>
            </VStack>
          </CardBody>
        </Card>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </VStack>
      </ResponsiveLayout>
    );
  };

  export default ExplorerPage;
