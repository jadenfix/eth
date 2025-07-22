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
import { CheckCircleIcon, PhoneIcon, SunIcon } from '@chakra-ui/icons';

const VoiceOpsPage: React.FC = () => {
  return (
    <ResponsiveLayout
      title="VoiceOps Service | API Layer"
      description="Voice-powered operations with ElevenLabs TTS/STT integration"
    >
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center" py={8}>
          <HStack justify="center" spacing={4} mb={4}>
            <Text fontSize="4xl">🎤</Text>
            <Text fontSize="3xl" fontWeight="bold">
              VoiceOps Service
            </Text>
            <Badge colorScheme="blue" size="lg">ElevenLabs</Badge>
          </HStack>
          <Text fontSize="lg" color="gray.600" maxW="3xl" mx="auto">
            Voice-powered operations with advanced text-to-speech alerts and speech-to-text command processing
          </Text>
        </Box>

        {/* Voice Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Voice Commands</StatLabel>
                <StatNumber>2,847</StatNumber>
                <StatHelpText>Processed today</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Recognition Accuracy</StatLabel>
                <StatNumber>97.3%</StatNumber>
                <StatHelpText>STT precision</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Response Time</StatLabel>
                <StatNumber>380ms</StatNumber>
                <StatHelpText>Average latency</StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <Stat>
                <StatLabel>Active Sessions</StatLabel>
                <StatNumber>47</StatNumber>
                <StatHelpText>Current users</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Voice Controls */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Voice System Configuration</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Voice Alerts</FormLabel>
                  <Switch defaultChecked colorScheme="green" />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Command Recognition</FormLabel>
                  <Switch defaultChecked colorScheme="blue" />
                </FormControl>

                <FormControl display="flex" alignItems="center">
                  <FormLabel mb="0">Real-time TTS</FormLabel>
                  <Switch defaultChecked colorScheme="purple" />
                </FormControl>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>

        {/* Voice Features */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🔊</Text>
                  <Text fontSize="xl" fontWeight="bold">Text-to-Speech Alerts</Text>
                </HStack>
                <Text color="gray.600">
                  Intelligent voice alerts for critical blockchain events
                </Text>
                
                <Box w="full">
                  <Text fontSize="sm" mb={2}>Voice Quality</Text>
                  <Progress value={96} colorScheme="green" mb={2} />
                  <Text fontSize="xs" color="gray.500">96% naturalness score</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    MEV opportunity alerts
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    Large transaction notifications
                  </ListItem>
                  <ListItem>
                    <ListIcon as={SunIcon} color="yellow.500" />
                    System status updates
                  </ListItem>
                  <ListItem>
                    <ListIcon as={PhoneIcon} color="purple.500" />
                    Custom alert rules
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <VStack align="start" spacing={4}>
                <HStack>
                  <Text fontSize="2xl">🎙️</Text>
                  <Text fontSize="xl" fontWeight="bold">Speech-to-Text Commands</Text>
                </HStack>
                <Text color="gray.600">
                  Natural language command processing for hands-free operation
                </Text>

                <Box w="full">
                  <Text fontSize="sm" mb={2}>Command Accuracy</Text>
                  <Progress value={97} colorScheme="blue" mb={2} />
                  <Text fontSize="xs" color="gray.500">97.3% recognition rate</Text>
                </Box>

                <List spacing={2}>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    "Show MEV activity"
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="blue.500" />
                    "Query top gas spenders"
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="purple.500" />
                    "Create new alert rule"
                  </ListItem>
                  <ListItem>
                    <ListIcon as={CheckCircleIcon} color="orange.500" />
                    "Export current view"
                  </ListItem>
                </List>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Voice Command Examples */}
        <Card>
          <CardBody>
            <VStack align="start" spacing={4}>
              <Text fontSize="xl" fontWeight="bold">Supported Voice Commands</Text>
              <Divider />
              
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4} w="full">
                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <Badge colorScheme="blue">Query</Badge>
                      <Text fontSize="sm" fontWeight="medium">
                        "Show me the top MEV bots from today"
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        Executes query and displays results
                      </Text>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <Badge colorScheme="green">Alert</Badge>
                      <Text fontSize="sm" fontWeight="medium">
                        "Alert me when gas price exceeds 100 gwei"
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        Creates new alert rule
                      </Text>
                    </VStack>
                  </CardBody>
                </Card>

                <Card variant="outline">
                  <CardBody>
                    <VStack align="start" spacing={2}>
                      <Badge colorScheme="purple">Navigate</Badge>
                      <Text fontSize="sm" fontWeight="medium">
                        "Open the compliance dashboard"
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        Navigation to specific pages
                      </Text>
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
                  <Text fontWeight="semibold">Voice Processing</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• ElevenLabs TTS/STT APIs</ListItem>
                    <ListItem>• WebRTC real-time audio</ListItem>
                    <ListItem>• Natural language understanding</ListItem>
                    <ListItem>• Intent classification models</ListItem>
                  </List>
                </VStack>

                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Integration Layer</Text>
                  <List spacing={1} fontSize="sm">
                    <ListItem>• WebSocket voice streaming</ListItem>
                    <ListItem>• REST API command execution</ListItem>
                    <ListItem>• Slack/Teams voice bot</ListItem>
                    <ListItem>• Mobile app integration</ListItem>
                  </List>
                </VStack>
              </SimpleGrid>

              <Box pt={4}>
                <Button colorScheme="blue" size="sm" mr={4}>
                  Test Voice Commands
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

export default VoiceOpsPage;
