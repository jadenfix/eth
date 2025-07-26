import React, { useState } from 'react';
import { useRouter } from 'next/router';
import {
  Box,
  Flex,
  HStack,
  VStack,
  Text,
  Button,
  IconButton,
  useColorModeValue,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  List,
  ListItem,
  Divider,
  Badge,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useToast,
} from '@chakra-ui/react';
import {
  FiMenu,
  FiX,
  FiHome,
  FiActivity,
  FiShield,
  FiUsers,
  FiZap,
  FiBarChart,
  FiGlobe,
  FiSettings,
  FiHeadphones,
  FiMonitor,
  FiDatabase,
  FiCpu,
  FiAward,
  FiStar,
  FiCheckCircle,
  FiBell,
  FiSearch,
  FiPocket,
  FiArrowRight,
} from 'react-icons/fi';

interface NavigationItem {
  name: string;
  path: string;
  icon: React.ComponentType<any>;
  description: string;
  badge?: string;
  color: string;
}

const navigationItems: NavigationItem[] = [
  {
    name: 'Dashboard',
    path: '/',
    icon: FiHome,
    description: 'Main overview and quick actions',
    color: 'blue',
  },
  {
    name: 'Live Data',
    path: '/live-data',
    icon: FiActivity,
    description: 'Real-time blockchain monitoring',
    badge: 'LIVE',
    color: 'green',
  },
  {
    name: 'MEV Intelligence',
    path: '/mev',
    icon: FiZap,
    description: 'Front-running and arbitrage detection',
    color: 'orange',
  },
  {
    name: 'Entity Resolution',
    path: '/intelligence/entities',
    icon: FiUsers,
    description: 'AI-powered address clustering',
    color: 'purple',
  },
  {
    name: 'Security & Compliance',
    path: '/compliance',
    icon: FiShield,
    description: 'OFAC screening and audit trails',
    color: 'red',
  },
  {
    name: 'Analytics',
    path: '/analytics',
    icon: FiBarChart,
    description: 'Advanced analytics and insights',
    color: 'teal',
  },
  {
    name: 'Visualization',
    path: '/canvas',
    icon: FiGlobe,
    description: '3D graphs and interactive charts',
    color: 'cyan',
  },
  {
    name: 'Voice Commands',
    path: '/voice',
    icon: FiHeadphones,
    description: 'Natural language interface',
    color: 'pink',
  },
  {
    name: 'System Monitoring',
    path: '/monitoring',
    icon: FiMonitor,
    description: 'Health and performance metrics',
    color: 'gray',
  },
  {
    name: 'Settings',
    path: '/workspace',
    icon: FiSettings,
    description: 'Configuration and preferences',
    color: 'gray',
  },
];

const CleanNavigation: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isOpen: isDrawerOpen, onOpen: onDrawerOpen, onClose: onDrawerClose } = useDisclosure();
  const toast = useToast();
  const router = useRouter();

  const bg = useColorModeValue('white', 'palantir.navy');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedTextColor = useColorModeValue('gray.600', 'gray.300');
  const hoverBg = useColorModeValue('gray.50', 'palantir.navy-light');

  const handleNavigation = (item: NavigationItem) => {
    // Navigate to the actual page
    router.push(item.path);
    onDrawerClose();
  };

  return (
    <>
      {/* Desktop Navigation */}
      <Box
        as="nav"
        position="fixed"
        top={0}
        left={0}
        right={0}
        zIndex={1000}
        borderBottom="1px"
        borderColor={borderColor}
        backdropFilter="blur(10px)"
        bg={useColorModeValue('rgba(255, 255, 255, 0.95)', 'rgba(26, 32, 44, 0.95)')}
      >
        <Flex justify="space-between" align="center" px={6} py={3}>
          {/* Logo and Brand */}
          <HStack spacing={4}>
            <HStack spacing={3}>
              <Box
                as={FiPocket}
                color="blue.500"
                boxSize={8}
              />
              <VStack align="start" spacing={0}>
                <Text fontWeight="bold" fontSize="lg" color={textColor}>
                  Onchain Command Center
                </Text>
                <Text fontSize="xs" color={mutedTextColor}>
                  Enterprise Blockchain Intelligence
                </Text>
              </VStack>
            </HStack>
            <Badge colorScheme="green" variant="subtle" fontSize="xs">
              <FiCheckCircle style={{ marginRight: '4px' }} />
              LIVE
            </Badge>
          </HStack>

          {/* Desktop Navigation Items */}
          <HStack spacing={1} display={{ base: 'none', lg: 'flex' }}>
            {navigationItems.slice(0, 6).map((item) => (
              <Button
                key={item.name}
                variant="ghost"
                size="sm"
                leftIcon={<item.icon />}
                onClick={() => handleNavigation(item)}
                _hover={{ bg: hoverBg }}
                color={textColor}
              >
                {item.name}
                {item.badge && (
                  <Badge ml={2} colorScheme="green" size="sm">
                    {item.badge}
                  </Badge>
                )}
              </Button>
            ))}
          </HStack>

          {/* Right Side Actions */}
          <HStack spacing={3}>
            <IconButton
              aria-label="Search"
              icon={<FiSearch />}
              variant="ghost"
              size="sm"
            />
            <IconButton
              aria-label="Notifications"
              icon={<FiBell />}
              variant="ghost"
              size="sm"
            />
            <Menu>
              <MenuButton
                as={Button}
                variant="ghost"
                size="sm"
                rightIcon={<FiArrowRight />}
              >
                More
              </MenuButton>
              <MenuList>
                {navigationItems.slice(6).map((item) => (
                  <MenuItem
                    key={item.name}
                    icon={<item.icon />}
                    onClick={() => handleNavigation(item)}
                  >
                    {item.name}
                  </MenuItem>
                ))}
              </MenuList>
            </Menu>
            <Button
              colorScheme="blue"
              size="sm"
              leftIcon={<FiStar />}
              onClick={() => handleNavigation({ name: 'Demo', path: '/demo', icon: FiStar, description: 'Full demo experience', color: 'blue' })}
            >
              Demo
            </Button>
          </HStack>

          {/* Mobile Menu Button */}
          <IconButton
            aria-label="Open menu"
            icon={<FiMenu />}
            variant="ghost"
            size="sm"
            display={{ base: 'flex', lg: 'none' }}
            onClick={onDrawerOpen}
          />
        </Flex>
      </Box>

      {/* Mobile Drawer */}
      <Drawer isOpen={isDrawerOpen} placement="right" onClose={onDrawerClose}>
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">
            <HStack spacing={3}>
              <Box as={FiPocket} color="blue.500" boxSize={6} />
              <Text fontWeight="bold">Navigation</Text>
            </HStack>
          </DrawerHeader>

          <DrawerBody p={0}>
            <List spacing={0}>
              {navigationItems.map((item, index) => (
                <ListItem key={item.name}>
                  <Button
                    w="full"
                    variant="ghost"
                    justifyContent="start"
                    py={4}
                    px={6}
                    leftIcon={<item.icon color={`${item.color}.500`} />}
                    onClick={() => handleNavigation(item)}
                    _hover={{ bg: hoverBg }}
                    borderRadius={0}
                  >
                    <VStack align="start" spacing={1} flex={1}>
                      <HStack justify="space-between" w="full">
                        <Text fontWeight="medium" color={textColor}>
                          {item.name}
                        </Text>
                        {item.badge && (
                          <Badge colorScheme="green" size="sm">
                            {item.badge}
                          </Badge>
                        )}
                      </HStack>
                      <Text fontSize="xs" color={mutedTextColor}>
                        {item.description}
                      </Text>
                    </VStack>
                  </Button>
                  {index < navigationItems.length - 1 && <Divider />}
                </ListItem>
              ))}
            </List>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Spacer for fixed navigation */}
      <Box h="80px" />
    </>
  );
};

export default CleanNavigation; 