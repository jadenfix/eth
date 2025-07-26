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
import { CheckCircleIcon, ViewIcon, SearchIcon } from '@chakra-ui/icons';

const EntityResolutionPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="Entity Resolution | Intelligence Layer"
      description="AI-powered entity matching and resolution using Vertex AI"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">🔍</Text>
            <Text fontSize="3xl" fontWeight="bold">
              Entity Resolution Pipeline
            </Text>
            <Badge colorScheme="orange" size="lg">Vertex AI</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Advanced entity matching and resolution pipeline using machine learning to identify and cluster blockchain entities
          </Text>
        </Box>

        {/* Pipeline Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Entities Processed</StatLabel>
                <StatNumber>2.4M</StatNumber>
                <StatHelpText>Total blockchain entities</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Match Accuracy</StatLabel>
                <StatNumber>94.7%</StatNumber>
                <StatHelpText>AI model precision</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Processing Speed</StatLabel>
                <StatNumber>15K/sec</StatNumber>
                <StatHelpText>Entities per second</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Clusters Found</StatLabel>
                <StatNumber>847K</StatNumber>
                <StatHelpText>Unique entity groups</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Pipeline Stages */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Resolution Pipeline Stages</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
                <VStack align="start" spacing={3}>
                  <HStack>
                    <Text fontSize="xl">📊</Text>
                    <Text fontWeight="semibold">Data Preprocessing</Text>
                  </HStack>
                  <Progress value={100} colorScheme="green" size="sm" />
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Address normalization</ListItem>
                    <ListItem>• Transaction pattern analysis</ListItem>
                    <ListItem>• Feature vector generation</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={3}>
                  <HStack>
                    <Text fontSize="xl">🤖</Text>
                    <Text fontWeight="semibold">AI Matching</Text>
                  </HStack>
                  <Progress value={87} colorScheme="blue" size="sm" />
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Vertex AI ML models</ListItem>
                    <ListItem>• Similarity scoring</ListItem>
                    <ListItem>• Confidence thresholding</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={3}>
                  <HStack>
                    <Text fontSize="xl">🔗</Text>
                    <Text fontWeight="semibold">Graph Storage</Text>
                  </HStack>
                  <Progress value={92} colorScheme="purple" size="sm" />
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Neo4j cluster creation</ListItem>
                    <ListItem>• Relationship mapping</ListItem>
                    <ListItem>• Entity ID assignment</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* AI Models & Features */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🧠</Text>
                  <Text fontSize="xl" fontWeight="bold">Machine Learning Models</Text>
                </HStack>
                <Text color="gray.600">
                  Advanced ML algorithms for entity identification and clustering
                </Text>
                
                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Graph Neural Networks (GNN)
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    BERT-based address embeddings
                  </ListItem>
                  <ListItem>
                    <ListIcon as={ViewIcon} color="purple.500" />
                    Behavioral pattern analysis
                  </ListItem>
                  <ListItem>
                    <ListIcon as={SearchIcon} color="orange.500" />
                    Fuzzy string matching
                  </ListItem>
                </List>

                <Box w="full">
                  <Text fontSize="sm" mb={2}>Model Performance</Text>
                  <Progress value={94} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">94.7% accuracy</Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🎯</Text>
                  <Text fontSize="xl" fontWeight="bold">Entity Types</Text>
                </HStack>
                <Text color="gray.600">
                  Comprehensive entity classification and clustering
                </Text>
                
                <SimpleGrid columns={2} spacing={3} w="full">
                  <VStack>
                    <Badge colorScheme="blue" size="lg">EOA</Badge>
                    <Text fontSize="sm">1.8M entities</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="purple" size="lg">Contracts</Badge>
                    <Text fontSize="sm">456K entities</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="green" size="lg">Exchanges</Badge>
                    <Text fontSize="sm">2.1K entities</Text>
                  </VStack>
                  <VStack>
                    <Badge colorScheme="orange" size="lg">DeFi</Badge>
                    <Text fontSize="sm">89K entities</Text>
                  </VStack>
                </SimpleGrid>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Technical Architecture */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Technical Architecture</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">AI/ML Stack</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Google Vertex AI Pipelines</ListItem>
                    <ListItem>• TensorFlow for deep learning</ListItem>
                    <ListItem>• Kubeflow for orchestration</ListItem>
                    <ListItem>• MLflow for experiment tracking</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Data Pipeline</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• BigQuery feature store</ListItem>
                    <ListItem>• Dataflow processing</ListItem>
                    <ListItem>• Neo4j graph storage</ListItem>
                    <ListItem>• Pub/Sub event streaming</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="orange" size="sm" mr={4}>
                  Run Pipeline
                </Button>
                <Button variant="outline" size="sm">
                  View Results
                </Button>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default EntityResolutionPage;
