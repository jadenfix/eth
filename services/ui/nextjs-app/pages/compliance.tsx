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
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon, InfoIcon } from '@chakra-ui/icons';

const CompliancePage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="Compliance Mapping | Onchain Command Center"
      description="Choropleth maps and Sankey diagrams for regulatory compliance analysis"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">🗺️</Text>
            <Text fontSize="3xl" fontWeight="bold">
              Compliance Mapping Service
            </Text>
            <Badge colorScheme="green" size="lg">Active</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Advanced regulatory compliance visualization using choropleth maps and Sankey diagrams for fund flow analysis
          </Text>
        </Box>

        {/* Key Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Jurisdictions Mapped</StatLabel>
                <StatNumber>195</StatNumber>
                <StatHelpText>Regulatory frameworks</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Compliance Rules</StatLabel>
                <StatNumber>2,847</StatNumber>
                <StatHelpText>Active monitoring</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Risk Assessments</StatLabel>
                <StatNumber>156K</StatNumber>
                <StatHelpText>Daily evaluations</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Alerts Generated</StatLabel>
                <StatNumber>342</StatNumber>
                <StatHelpText>Last 24 hours</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Features Grid */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Choropleth Mapping */}
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🌍</Text>
                  <Text fontSize="xl" fontWeight="bold">Choropleth Maps</Text>
                </HStack>
                <Text color="gray.600">
                  Geographic visualization of regulatory compliance across jurisdictions
                </Text>
                
                <Box w="full">
                  <Text fontSize="sm" mb={2}>Compliance Coverage</Text>
                  <Progress value={94} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">94% global coverage</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Real-time regulatory mapping
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Risk heatmaps by jurisdiction
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Interactive drill-down
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          {/* Sankey Diagrams */}
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🌊</Text>
                  <Text fontSize="xl" fontWeight="bold">Sankey Diagrams</Text>
                </HStack>
                <Text color="gray.600">
                  Fund flow analysis and transaction path visualization
                </Text>

                <Box w="full">
                  <Text fontSize="sm" mb={2}>Flow Analysis</Text>
                  <Progress value={87} colorScheme="blue" mb={2} />
                  <Text fontSize="xs" color="gray.500">87% path resolution</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Multi-hop transaction tracking
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Cross-chain flow analysis
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Regulatory breach detection
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Recent Alerts */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Recent Compliance Alerts</Text>
              <Divider />
              
              <VStack align="start" spacing={3} w="full">
                <HStack justify="space-between" w="full">
                  <HStack>
                    <WarningIcon color="yellow.500" />
                    <Text>High-risk jurisdiction transaction detected</Text>
                  </HStack>
                  <Badge colorScheme="yellow">Medium</Badge>
                </HStack>

                <HStack justify="space-between" w="full">
                  <HStack>
                    <InfoIcon color="blue.500" />
                    <Text>New regulatory framework update: EU MiCA</Text>
                  </HStack>
                  <Badge colorScheme="blue">Info</Badge>
                </HStack>

                <HStack justify="space-between" w="full">
                  <HStack>
                    <WarningIcon color="red.500" />
                    <Text>Sanctioned entity interaction flagged</Text>
                  </HStack>
                  <Badge colorScheme="red">High</Badge>
                </HStack>
              </VStack>

              <Button colorScheme="blue" size="sm">
                View All Alerts
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {/* Technical Specifications */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Technical Specifications</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Visualization Engine</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• D3.js choropleth rendering</ListItem>
                    <ListItem>• Interactive Sankey diagrams</ListItem>
                    <ListItem>• WebGL acceleration</ListItem>
                    <ListItem>• Real-time data binding</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Data Processing</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• BigQuery compliance queries</ListItem>
                    <ListItem>• Neo4j relationship analysis</ListItem>
                    <ListItem>• DLP policy enforcement</ListItem>
                    <ListItem>• Vertex AI risk scoring</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default CompliancePage;
