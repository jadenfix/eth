/**
 * Activity Drawer
 * Right fly-out drawer for recent activity and notifications
 */

import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Avatar,
  Divider,
  IconButton,
  useColorMode,
} from '@chakra-ui/react';
import { CloseIcon, ExternalLinkIcon } from '@chakra-ui/icons';
import { motion, AnimatePresence } from 'framer-motion';

const MotionBox = motion(Box);
const MotionVStack = motion(VStack);

interface ActivityItem {
  id: string;
  type: 'transaction' | 'alert' | 'system' | 'user';
  title: string;
  description: string;
  timestamp: string;
  avatar?: string;
  status?: 'success' | 'warning' | 'error' | 'info';
}

interface ActivityDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const sampleActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'alert',
    title: 'High Risk Transaction Detected',
    description: 'Large transfer to sanctioned address detected',
    timestamp: '2 minutes ago',
    status: 'error',
  },
  {
    id: '2',
    type: 'transaction',
    title: 'Entity Relationship Updated',
    description: 'New connection discovered between wallet_1 and exchange_1',
    timestamp: '5 minutes ago',
    status: 'info',
  },
  {
    id: '3',
    type: 'system',
    title: 'Neo4j Sync Complete',
    description: 'Successfully synced 1,247 entities from BigQuery',
    timestamp: '10 minutes ago',
    status: 'success',
  },
  {
    id: '4',
    type: 'user',
    title: 'Workspace Layout Saved',
    description: 'Custom dashboard layout has been saved',
    timestamp: '15 minutes ago',
    status: 'info',
  },
  {
    id: '5',
    type: 'alert',
    title: 'Compliance Violation',
    description: 'Transaction exceeds jurisdiction limit',
    timestamp: '20 minutes ago',
    status: 'warning',
  },
];

const ActivityDrawer: React.FC<ActivityDrawerProps> = ({ isOpen, onClose }) => {
  const { colorMode } = useColorMode();

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'success': return 'green';
      case 'warning': return 'yellow';
      case 'error': return 'red';
      case 'info': return 'blue';
      default: return 'gray';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'transaction': return '💸';
      case 'alert': return '🚨';
      case 'system': return '⚙️';
      case 'user': return '👤';
      default: return '📝';
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <MotionBox
          position="fixed"
          top="48px"
          right={0}
          w="320px"
          h="calc(100vh - 48px)"
          bg={colorMode === 'dark' ? 'palantir.navy-light' : 'white'}
          borderLeft="1px solid"
          borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.200'}
          boxShadow="xl"
          zIndex={1000}
          initial={{ x: 320 }}
          animate={{ x: 0 }}
          exit={{ x: 320 }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        >
          {/* Header */}
          <HStack justify="space-between" p={4} borderBottom="1px solid" borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.200'}>
            <VStack align="start" spacing={0}>
              <Text fontSize="lg" fontWeight="bold">
                Recent Activity
              </Text>
              <Text fontSize="sm" color="gray.500">
                Live updates and notifications
              </Text>
            </VStack>
            <IconButton
              aria-label="Close activity drawer"
              icon={<CloseIcon />}
              size="sm"
              variant="ghost"
              onClick={onClose}
            />
          </HStack>

          {/* Activity List */}
          <Box flex="1" overflow="auto">
            <MotionVStack
              spacing={0}
              align="stretch"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              {sampleActivities.map((activity, index) => (
                <MotionBox
                  key={activity.id}
                  p={4}
                  borderBottom="1px solid"
                  borderColor={colorMode === 'dark' ? 'gray.700' : 'gray.100'}
                  cursor="pointer"
                  _hover={{
                    bg: colorMode === 'dark' ? 'gray.700' : 'gray.50',
                  }}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.02 }}
                >
                  <HStack spacing={3} align="start">
                    {/* Icon/Avatar */}
                    <Box
                      w={8}
                      h={8}
                      borderRadius="full"
                      bg={`${getStatusColor(activity.status)}.100`}
                      color={`${getStatusColor(activity.status)}.600`}
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      fontSize="sm"
                      flexShrink={0}
                    >
                      {getTypeIcon(activity.type)}
                    </Box>

                    {/* Content */}
                    <VStack align="start" spacing={1} flex="1" minW={0}>
                      <HStack justify="space-between" w="100%">
                        <Text fontSize="sm" fontWeight="600" noOfLines={1}>
                          {activity.title}
                        </Text>
                        <IconButton
                          aria-label="Open details"
                          icon={<ExternalLinkIcon />}
                          size="xs"
                          variant="ghost"
                          opacity={0.6}
                          _hover={{ opacity: 1 }}
                        />
                      </HStack>
                      <Text fontSize="xs" color="gray.500" noOfLines={2}>
                        {activity.description}
                      </Text>
                      <HStack justify="space-between" w="100%">
                        <Text fontSize="xs" color="gray.400">
                          {activity.timestamp}
                        </Text>
                        {activity.status && (
                          <Badge
                            size="sm"
                            colorScheme={getStatusColor(activity.status)}
                            variant="subtle"
                          >
                            {activity.status}
                          </Badge>
                        )}
                      </HStack>
                    </VStack>
                  </HStack>
                </MotionBox>
              ))}
            </MotionVStack>
          </Box>

          {/* Footer */}
          <Box p={4} borderTop="1px solid" borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.200'}>
            <Text fontSize="xs" color="gray.500" textAlign="center">
              Auto-refreshes every 30 seconds
            </Text>
          </Box>
        </MotionBox>
      )}
    </AnimatePresence>
  );
};

export default ActivityDrawer;
