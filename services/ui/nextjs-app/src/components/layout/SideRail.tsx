/**
 * Collapsible Side Rail Navigation
 * Palantir-style navigation with smooth animations
 */

import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Icon,
  Tooltip,
  useColorMode,
  Divider,
} from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/router';
import Link from 'next/link';

const MotionBox = motion(Box);
const MotionVStack = motion(VStack);

interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: string;
  subItems?: NavItem[];
}

interface SideRailProps {
  isOpen: boolean;
  onToggle: () => void;
}

const navigationItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: '📊',
    path: '/',
  },
  {
    id: 'services',
    label: 'Services',
    icon: '🔧',
    path: '/services',
    subItems: [
      { id: 'graph-api', label: 'Graph API', icon: '🕸️', path: '/services/graph' },
      { id: 'voice-ops', label: 'Voice Ops', icon: '🎤', path: '/voice' },
      { id: 'ingestion', label: 'Ingestion', icon: '📥', path: '/ingestion' },
    ],
  },
  {
    id: 'architecture',
    label: 'Architecture',
    icon: '🏗️',
    path: '/architecture',
  },
  {
    id: 'graph',
    label: 'Graph Explorer',
    icon: '🕸️',
    path: '/explorer',
    badge: 'New',
  },
  {
    id: 'canvas',
    label: 'Time Canvas',
    icon: '📈',
    path: '/canvas',
  },
  {
    id: 'compliance',
    label: 'Compliance',
    icon: '🛡️',
    path: '/compliance',
  },
  {
    id: 'workspace',
    label: 'Workspace',
    icon: '🏠',
    path: '/workspace',
    badge: 'Beta',
  },
  {
    id: 'monitoring',
    label: 'Monitoring',
    icon: '📡',
    path: '/monitoring',
  },
];

const SideRail: React.FC<SideRailProps> = ({ isOpen }) => {
  const { colorMode } = useColorMode();
  const router = useRouter();

  const isActivePath = (path: string) => {
    return router.pathname === path || router.pathname.startsWith(path + '/');
  };

  const NavItemComponent = ({ item, isSubItem = false }: { item: NavItem; isSubItem?: boolean }) => {
    const isActive = isActivePath(item.path);

    return (
      <Link href={item.path} passHref>
        <Tooltip
          label={!isOpen ? item.label : ''}
          placement="right"
          hasArrow
          isDisabled={isOpen}
        >
          <MotionBox
            w="100%"
            cursor="pointer"
            borderRadius="lg"
            p={isOpen ? 3 : 2}
            mx={isSubItem ? 4 : 0}
            bg={isActive ? 'brand.500' : 'transparent'}
            color={isActive ? 'white' : colorMode === 'dark' ? 'gray.300' : 'gray.700'}
            _hover={{
              bg: isActive ? 'brand.600' : colorMode === 'dark' ? 'palantir.navy-light' : 'gray.100',
              transform: 'translateX(4px)',
            }}
            transition="all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <HStack spacing={3} justify={isOpen ? 'flex-start' : 'center'}>
              <Text fontSize={isSubItem ? 'sm' : 'lg'}>{item.icon}</Text>
              <AnimatePresence>
                {isOpen && (
                  <MotionBox
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <HStack spacing={2} flex="1">
                      <Text
                        fontSize="sm"
                        fontWeight={isActive ? '600' : '500'}
                        letterSpacing="tight"
                        noOfLines={1}
                      >
                        {item.label}
                      </Text>
                      {item.badge && (
                        <Box
                          bg={isActive ? 'white' : 'brand.500'}
                          color={isActive ? 'brand.500' : 'white'}
                          px={2}
                          py={1}
                          borderRadius="full"
                          fontSize="xs"
                          fontWeight="600"
                        >
                          {item.badge}
                        </Box>
                      )}
                    </HStack>
                  </MotionBox>
                )}
              </AnimatePresence>
            </HStack>
          </MotionBox>
        </Tooltip>
      </Link>
    );
  };

  return (
    <MotionBox
      as="nav"
      w={isOpen ? '280px' : '72px'}
      h="calc(100vh - 48px)"
      bg={colorMode === 'dark' ? 'palantir.navy' : 'white'}
      borderRight="1px solid"
      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.200'}
      position="sticky"
      top="48px"
      transition="width 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
      zIndex={999}
      initial={{ x: -280 }}
      animate={{ x: 0 }}
    >
      <MotionVStack
        spacing={1}
        p={4}
        align="stretch"
        h="100%"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {/* Primary Navigation */}
        <VStack spacing={1} align="stretch">
          {navigationItems.map((item) => (
            <Box key={item.id}>
              <NavItemComponent item={item} />
              {item.subItems && isOpen && isActivePath(item.path) && (
                <MotionBox
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  mt={1}
                >
                  <VStack spacing={1} align="stretch">
                    {item.subItems.map((subItem) => (
                      <NavItemComponent key={subItem.id} item={subItem} isSubItem />
                    ))}
                  </VStack>
                </MotionBox>
              )}
            </Box>
          ))}
        </VStack>

        {/* Spacer */}
        <Box flex="1" />

        {/* Status Section */}
        <AnimatePresence>
          {isOpen && (
            <MotionBox
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.2 }}
            >
              <Divider mb={4} />
              <VStack spacing={2} align="stretch">
                <HStack spacing={2}>
                  <Box w={2} h={2} borderRadius="full" bg="green.400" />
                  <Text fontSize="xs" color="gray.500">
                    All systems operational
                  </Text>
                </HStack>
                <HStack spacing={2}>
                  <Box w={2} h={2} borderRadius="full" bg="blue.400" />
                  <Text fontSize="xs" color="gray.500">
                    Real-time streaming active
                  </Text>
                </HStack>
                <HStack spacing={2}>
                  <Box w={2} h={2} borderRadius="full" bg="yellow.400" />
                  <Text fontSize="xs" color="gray.500">
                    Neo4j connected
                  </Text>
                </HStack>
              </VStack>
            </MotionBox>
          )}
        </AnimatePresence>
      </MotionVStack>
    </MotionBox>
  );
};

export default SideRail;
