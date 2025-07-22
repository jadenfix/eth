import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import {
  Box,
  Container,
  HStack,
  VStack,
  Text,
  Button,
  IconButton,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  useColorModeValue,
  Badge,
  Divider,
  Stack,
  Collapse,
} from '@chakra-ui/react';
import { HamburgerIcon, ChevronDownIcon, ChevronRightIcon } from '@chakra-ui/icons';

interface NavItem {
  label: string;
  href?: string;
  icon?: string;
  children?: NavItem[];
  badge?: string;
  badgeColor?: string;
}

const NAV_ITEMS: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/',
    icon: '🏠'
  },
  {
    label: 'Architecture',
    href: '/architecture',
    icon: '🏛️'
  },
  {
    label: 'Identity & Access',
    icon: '🛡️',
    children: [
      {
        label: 'Access Control',
        href: '/security/access',
        icon: '🔐',
        badge: 'SOC-2',
        badgeColor: 'red'
      },
      {
        label: 'Audit Logs',
        href: '/security/audit',
        icon: '📝'
      },
      {
        label: 'DLP Protection',
        href: '/security/dlp',
        icon: '�'
      }
    ]
  },
  {
    label: 'Ingestion Layer',
    icon: '📥',
    children: [
      {
        label: 'All Ingestion',
        href: '/ingestion',
        icon: '�📋'
      },
      {
        label: 'Ethereum Ingester',
        href: '/ingestion/ethereum',
        icon: '⛓️',
        badge: 'LIVE',
        badgeColor: 'green'
      },
      {
        label: 'Data Pipeline',
        href: '/ingestion/pipeline',
        icon: '🔄'
      },
      {
        label: 'TheGraph Integration',
        href: '/ingestion/thegraph',
        icon: '�️'
      }
    ]
  },
  {
    label: 'Semantic Fusion',
    icon: '🧠',
    children: [
      {
        label: 'Ontology Service',
        href: '/ontology',
        icon: '🗺️',
        badge: 'GraphQL',
        badgeColor: 'purple'
      },
      {
        label: 'Entity Resolution',
        href: '/intelligence/entities',
        icon: '🔍',
        badge: 'AI',
        badgeColor: 'orange'
      },
      {
        label: 'Graph Explorer',
        href: '/explorer',
        icon: '🌐'
      }
    ]
  },
  {
    label: 'Intelligence Mesh',
    icon: '🤖',
    children: [
      {
        label: 'MEV Watch Agent',
        href: '/mev',
        icon: '👁️',
        badge: 'ACTIVE',
        badgeColor: 'green'
      },
      {
        label: 'Whale Tracker',
        href: '/agents/whale',
        icon: '🐋'
      },
      {
        label: 'Sanctions Alert',
        href: '/agents/sanctions',
        icon: '⚠️'
      },
      {
        label: 'Risk AI Models',
        href: '/intelligence/risk',
        icon: '🎯'
      },
      {
        label: 'Anomaly Detection',
        href: '/intelligence/anomaly',
        icon: '🚨'
      }
    ]
  },
  {
    label: 'API & VoiceOps',
    icon: '🔗',
    children: [
      {
        label: 'API Gateway',
        href: '/api/gateway',
        icon: '🚪'
      },
      {
        label: 'GraphQL API',
        href: '/api/graphql',
        icon: '📊'
      },
      {
        label: 'WebSocket Streams',
        href: '/api/websocket',
        icon: '⚡'
      },
      {
        label: 'VoiceOps Service',
        href: '/voice',
        icon: '🎤',
        badge: 'ElevenLabs',
        badgeColor: 'blue'
      }
    ]
  },
  {
    label: 'Visualization',
    icon: '📈',
    children: [
      {
        label: 'Analytics Dashboard',
        href: '/analytics',
        icon: '📊'
      },
      {
        label: 'Time Series Canvas',
        href: '/canvas',
        icon: '📈'
      },
      {
        label: 'Compliance Maps',
        href: '/compliance',
        icon: '🗺️'
      },
      {
        label: 'DeckGL Explorer',
        href: '/explorer/deckgl',
        icon: '🌍'
      },
      {
        label: 'Network Graphs',
        href: '/visualization/network',
        icon: '�️'
      }
    ]
  },
  {
    label: 'Workflow Builder',
    icon: '🔄',
    children: [
      {
        label: 'Foundry Workspace',
        href: '/workspace',
        icon: '�️',
        badge: 'NEW',
        badgeColor: 'purple'
      },
      {
        label: 'Signal Builder',
        href: '/workflows/signals',
        icon: '⚙️'
      },
      {
        label: 'Dagster Pipelines',
        href: '/workflows/dagster',
        icon: '🔗'
      },
      {
        label: 'Status Dashboard',
        href: '/dashboard/status',
        icon: '📋'
      }
    ]
  },
  {
    label: 'Monitoring',
    icon: '📡',
    children: [
      {
        label: 'System Health',
        href: '/monitoring',
        icon: '💚'
      },
      {
        label: 'Performance Metrics',
        href: '/monitoring/metrics',
        icon: '📈'
      },
      {
        label: 'Alert Management',
        href: '/monitoring/alerts',
        icon: '🚨'
      }
    ]
  }
];

interface DesktopNavProps {
  navItems: NavItem[];
}

const DesktopNav: React.FC<DesktopNavProps> = ({ navItems }) => {
  const router = useRouter();
  const linkColor = useColorModeValue('gray.600', 'gray.200');
  const linkHoverColor = useColorModeValue('gray.800', 'white');
  const popoverContentBgColor = useColorModeValue('white', 'gray.800');
  const [openPopover, setOpenPopover] = useState<string | null>(null);

  const handlePopoverToggle = (label: string) => {
    setOpenPopover(openPopover === label ? null : label);
  };

  return (
    <HStack spacing={1}>
      {/* Quick Services Link */}
      <Link href="/services">
        <Button
          variant={router.pathname === '/services' ? 'solid' : 'ghost'}
          colorScheme={router.pathname === '/services' ? 'blue' : 'gray'}
          size="sm"
          leftIcon={<Text>📋</Text>}
        >
          Services
        </Button>
      </Link>
      
      {navItems.map((navItem) => (
        <Box key={navItem.label} position="relative">
          {navItem.children ? (
            <Box>
              <Button
                variant="ghost"
                size="sm"
                leftIcon={navItem.icon ? <Text>{navItem.icon}</Text> : undefined}
                rightIcon={navItem.children ? <ChevronDownIcon /> : undefined}
                onClick={() => handlePopoverToggle(navItem.label)}
                _hover={{ bg: 'gray.100' }}
              >
                {navItem.label}
                {navItem.badge && (
                  <Badge ml={2} colorScheme={navItem.badgeColor} size="xs">
                    {navItem.badge}
                  </Badge>
                )}
              </Button>
              
              {openPopover === navItem.label && (
                <Box
                  position="absolute"
                  top="100%"
                  left={0}
                  zIndex={1000}
                  bg={popoverContentBgColor}
                  shadow="lg"
                  borderRadius="md"
                  border="1px solid"
                  borderColor="gray.200"
                  minW="250px"
                  p={4}
                  mt={1}
                >
                  <VStack align="stretch" spacing={2}>
                    {navItem.children.map((child) => (
                      <Link key={child.label} href={child.href ?? '#'}>
                        <HStack
                          spacing={3}
                          p={2}
                          borderRadius="md"
                          _hover={{ bg: 'gray.50' }}
                          cursor="pointer"
                          onClick={() => setOpenPopover(null)}
                        >
                          {child.icon && <Text>{child.icon}</Text>}
                          <VStack align="start" spacing={0} flex={1}>
                            <HStack>
                              <Text fontSize="sm" fontWeight="medium">
                                {child.label}
                              </Text>
                              {child.badge && (
                                <Badge colorScheme={child.badgeColor} size="xs">
                                  {child.badge}
                                </Badge>
                              )}
                            </HStack>
                          </VStack>
                        </HStack>
                      </Link>
                    ))}
                  </VStack>
                </Box>
              )}
            </Box>
          ) : (
            <Link href={navItem.href ?? '#'}>
              <Button
                variant={router.pathname === navItem.href ? 'solid' : 'ghost'}
                colorScheme={router.pathname === navItem.href ? 'blue' : 'gray'}
                size="sm"
                leftIcon={navItem.icon ? <Text>{navItem.icon}</Text> : undefined}
              >
                {navItem.label}
                {navItem.badge && (
                  <Badge ml={2} colorScheme={navItem.badgeColor} size="xs">
                    {navItem.badge}
                  </Badge>
                )}
              </Button>
            </Link>
          )}
        </Box>
      ))}
    </HStack>
  );
};

interface MobileNavItemProps {
  label: string;
  children?: NavItem[];
  href?: string;
  icon?: string;
  badge?: string;
  badgeColor?: string;
  onClose: () => void;
}

const MobileNavItem: React.FC<MobileNavItemProps> = ({
  label,
  children,
  href,
  icon,
  badge,
  badgeColor,
  onClose,
}) => {
  const { isOpen, onToggle } = useDisclosure();
  const router = useRouter();

  const handleClick = () => {
    if (href) {
      onClose();
      router.push(href);
    } else if (children) {
      onToggle();
    }
  };

  return (
    <Stack spacing={4} onClick={handleClick}>
      <HStack justify="space-between" align="center">
        <HStack spacing={3}>
          {icon && <Text fontSize="lg">{icon}</Text>}
          <Text fontWeight={600} color="gray.600">
            {label}
          </Text>
          {badge && (
            <Badge colorScheme={badgeColor} size="sm">
              {badge}
            </Badge>
          )}
        </HStack>
        {children && (
          <IconButton
            onClick={onToggle}
            icon={isOpen ? <ChevronDownIcon /> : <ChevronRightIcon />}
            variant="ghost"
            size="sm"
            aria-label="Toggle Navigation"
          />
        )}
      </HStack>

      <Collapse in={isOpen} animateOpacity style={{ marginTop: '0!important' }}>
        <Stack
          mt={2}
          pl={4}
          borderLeft={1}
          borderStyle="solid"
          borderColor="gray.200"
          align="start"
        >
          {children &&
            children.map((child) => (
              <Link key={child.label} href={child.href ?? '#'}>
                <HStack spacing={2} py={2} onClick={onClose}>
                  {child.icon && <Text>{child.icon}</Text>}
                  <Text fontSize="sm" color="gray.500">
                    {child.label}
                  </Text>
                  {child.badge && (
                    <Badge colorScheme={child.badgeColor} size="xs">
                      {child.badge}
                    </Badge>
                  )}
                </HStack>
              </Link>
            ))}
        </Stack>
      </Collapse>
    </Stack>
  );
};

interface MobileNavProps {
  isOpen: boolean;
  onClose: () => void;
}

const MobileNav: React.FC<MobileNavProps> = ({ isOpen, onClose }) => {
  return (
    <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="xs">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader borderBottomWidth="1px">
          <HStack spacing={2}>
            <Text fontSize="xl">⚡</Text>
            <VStack align="start" spacing={0}>
              <Text fontSize="lg" fontWeight="bold">
                Onchain Intel
              </Text>
              <Text fontSize="xs" color="gray.500">
                Command Center
              </Text>
            </VStack>
          </HStack>
        </DrawerHeader>

        <DrawerBody>
          <Stack spacing={4} mt={4}>
            {/* Quick Access */}
            <Link href="/services">
              <HStack 
                spacing={3} 
                p={3} 
                bg="blue.50" 
                borderRadius="md" 
                onClick={onClose}
                cursor="pointer"
                _hover={{ bg: 'blue.100' }}
              >
                <Text fontSize="lg">📋</Text>
                <VStack align="start" spacing={0}>
                  <Text fontWeight="600" color="blue.700" fontSize="sm">
                    All Services Overview
                  </Text>
                  <Text fontSize="xs" color="blue.500">
                    Complete platform overview
                  </Text>
                </VStack>
              </HStack>
            </Link>
            
            <Divider />
            
            {NAV_ITEMS.map((navItem) => (
              <MobileNavItem
                key={navItem.label}
                {...navItem}
                onClose={onClose}
              />
            ))}
            
            <Divider />
            
            <VStack spacing={3} align="stretch">
              <Text fontSize="xs" color="gray.500" textTransform="uppercase" fontWeight="bold">
                Platform Status
              </Text>
              <HStack justify="space-between">
                <Text fontSize="sm">System Health</Text>
                <Badge colorScheme="green" variant="solid">99.9%</Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Active Services</Text>
                <Badge colorScheme="blue" variant="solid">25+</Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Neo4j Status</Text>
                <Badge colorScheme="green" variant="solid">LIVE</Badge>
              </HStack>
              <HStack justify="space-between">
                <Text fontSize="sm">Vertex AI</Text>
                <Badge colorScheme="purple" variant="solid">READY</Badge>
              </HStack>
            </VStack>
          </Stack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  );
};

export const ResponsiveNavBar: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const router = useRouter();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const [isDesktop, setIsDesktop] = useState(false);

  useEffect(() => {
    const checkIfDesktop = () => {
      setIsDesktop(window.innerWidth >= 1024); // lg breakpoint
    };
    
    checkIfDesktop();
    window.addEventListener('resize', checkIfDesktop);
    
    return () => window.removeEventListener('resize', checkIfDesktop);
  }, []);

  return (
    <>
      <Box
        bg={bgColor}
        borderBottom="1px solid"
        borderColor={borderColor}
        position="sticky"
        top={0}
        zIndex={1000}
        shadow="sm"
      >
        <Container maxW="7xl" px={4}>
          <HStack h="60px" justify="space-between" align="center">
            {/* Logo */}
            <Link href="/">
              <HStack spacing={2} cursor="pointer">
                <Text fontSize="2xl">⚡</Text>
                <VStack align="start" spacing={0} display={{ base: 'none', md: 'flex' }}>
                  <Text fontSize="lg" fontWeight="bold">
                    Onchain Intelligence
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    Palantir-Grade Command Center
                  </Text>
                </VStack>
                <Text fontSize="md" fontWeight="bold" display={{ base: 'block', md: 'none' }}>
                  Onchain Intel
                </Text>
              </HStack>
            </Link>

            {/* Desktop Navigation */}
            {isDesktop && <DesktopNav navItems={NAV_ITEMS} />}

            {/* Mobile menu button */}
            <IconButton
              onClick={onOpen}
              icon={<HamburgerIcon />}
              variant="ghost"
              aria-label="Open Navigation"
              display={{ base: 'flex', lg: 'none' }}
            />
          </HStack>
        </Container>
      </Box>

      {/* Mobile Navigation */}
      <MobileNav isOpen={isOpen} onClose={onClose} />
    </>
  );
};
