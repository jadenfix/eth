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
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
} from '@chakra-ui/react';
import { CheckCircleIcon, LockIcon, WarningIcon } from '@chakra-ui/icons';

const AccessControlPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="Access Control | Security Layer"
      description="Fine-grained access control with role-based permissions and audit logging"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">🔐</Text>
            <Text fontSize="3xl" fontWeight="bold">
              Access Control System
            </Text>
            <Badge colorScheme="red" size="lg">SOC-2 Ready</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Enterprise-grade access control with Cloud IAM, BigQuery column-level ACLs, and comprehensive audit logging
          </Text>
        </Box>

        {/* Security Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Active Users</StatLabel>
                <StatNumber>247</StatNumber>
                <StatHelpText>Authenticated sessions</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Security Score</StatLabel>
                <StatNumber>98%</StatNumber>
                <StatHelpText>Compliance rating</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Failed Attempts</StatLabel>
                <StatNumber>0</StatNumber>
                <StatHelpText>Last 24 hours</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Audit Events</StatLabel>
                <StatNumber>1,423</StatNumber>
                <StatHelpText>This week</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Access Control Features */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🛡️</Text>
                  <Text fontSize="xl" fontWeight="bold">Role-Based Access</Text>
                </HStack>
                <Text color="gray.600">
                  Granular permissions with role inheritance and dynamic policies
                </Text>
                
                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={WarningIcon} color="red.500" />
                    Admin: Full platform access
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Analyst: Read/query permissions
                  </ListItem>
                  <ListItem>
                    <ListIcon as={LockIcon} color="blue.500" />
                    Viewer: Dashboard-only access
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    API: Service-to-service auth
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">📊</Text>
                  <Text fontSize="xl" fontWeight="bold">Data Governance</Text>
                </HStack>
                <Text color="gray.600">
                  Column-level security with DLP integration for sensitive data
                </Text>
                
                <Box w="full">
                  <Text fontSize="sm" mb={2}>Data Protection</Text>
                  <Progress value={96} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">96% coverage</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={LockIcon} color="red.500" />
                    PII data masking
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    Column-level ACLs
                  </ListItem>
                  <ListItem>
                    <ListIcon as={WarningIcon} color="blue.500" />
                    DLP redaction rules
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Recent Access Events */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Recent Access Events</Text>
              <Divider />
              
              <Table size="sm">
                <Thead>
                  <Tr>
                    <Th>User</Th>
                    <Th>Action</Th>
                    <Th>Resource</Th>
                    <Th>Status</Th>
                    <Th>Time</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td>analyst@company.com</Td>
                    <Td>query.execute</Td>
                    <Td>ethereum.transactions</Td>
                    <Td><Badge colorScheme="green">ALLOWED</Badge></Td>
                    <Td>2 min ago</Td>
                  </Tr>
                  <Tr>
                    <Td>viewer@company.com</Td>
                    <Td>dashboard.view</Td>
                    <Td>mev.analytics</Td>
                    <Td><Badge colorScheme="green">ALLOWED</Badge></Td>
                    <Td>5 min ago</Td>
                  </Tr>
                  <Tr>
                    <Td>api.service</Td>
                    <Td>data.ingest</Td>
                    <Td>blocks.raw</Td>
                    <Td><Badge colorScheme="green">ALLOWED</Badge></Td>
                    <Td>8 min ago</Td>
                  </Tr>
                </Tbody>
              </Table>
            </VStack>
          </CardBody>
        </Card>

        {/* Technical Stack */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Security Infrastructure</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Identity Management</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Google Cloud IAM integration</ListItem>
                    <ListItem>• OAuth 2.0 / OIDC authentication</ListItem>
                    <ListItem>• Multi-factor authentication</ListItem>
                    <ListItem>• Service account management</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Audit & Compliance</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• Cloud Logging integration</ListItem>
                    <ListItem>• SOC-2 audit trails</ListItem>
                    <ListItem>• Real-time security monitoring</ListItem>
                    <ListItem>• Compliance reporting</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="red" size="sm" mr={4}>
                  Manage Permissions
                </Button>
                <Button variant="outline" size="sm">
                  View Audit Logs
                </Button>
              </Box>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </ResponsiveLayout>
  );
};

export default AccessControlPage;
