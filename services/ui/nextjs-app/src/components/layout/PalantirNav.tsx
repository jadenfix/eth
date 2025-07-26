import React, { useState } from 'react';
import {
  Box,
  Flex,
  HStack,
  VStack,
  Text,
  IconButton,
  Button,
  useColorMode,
  useColorModeValue,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Divider,
  Badge,
  Tooltip,
  Avatar,
  Input,
  InputGroup,
  InputLeftElement,
} from '@chakra-ui/react';
import Link from 'next/link';
import { useRouter } from 'next/router';

// Icons (using simple text for now, can be replaced with actual icons)
const Icon = ({ children, ...props }: any) => (
  <Box as="span" fontSize="lg" {...props}>
    {children}
  </Box>
);

interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: string;
  children?: NavItem[];
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/',
    icon: 'D',
  },
  {
    label: 'Intelligence',
    href: '/intelligence',
    icon: 'I',
    children: [
      { label: 'MEV Detection', href: '/mev', icon: 'M' },
      { label: 'Entity Resolution', href: '/ontology', icon: 'E' },
      { label: 'Risk Analysis', href: '/analytics', icon: 'R' },
    ],
  },
  {
    label: 'Operations',
    href: '/operations',
    icon: 'O',
    children: [
      { label: 'Ingestion', href: '/ingestion', icon: 'I' },
      { label: 'Monitoring', href: '/monitoring', icon: 'M' },
      { label: 'Compliance', href: '/compliance', icon: 'C' },
    ],
  },
  {
    label: 'Workspace',
    href: '/workspace',
    icon: 'W',
    children: [
      { label: 'Canvas', href: '/canvas', icon: 'C' },
      { label: 'Explorer', href: '/explorer', icon: 'E' },
      { label: 'Voice', href: '/voice', icon: 'V' },
    ],
  },
  {
    label: 'Services',
    href: '/services',
    icon: 'S',
  },
  {
    label: 'Architecture',
    href: '/architecture',
    icon: 'A',
  },
];

const PalantirNav: React.FC = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  const bg = useColorModeValue('white', 'dark.800');
  const borderColor = useColorModeValue('gray.200', 'dark.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const hoverBg = useColorModeValue('gray.50', 'dark.700');

  const isActive = (href: string) => router.pathname === href;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  return (
    <Box position="fixed" top={0} left={0} right={0} zIndex={1000} bg={bg} borderBottom="1px solid" borderColor={borderColor}>
      {/* Top Navigation Bar */}
      <Flex h="60px" px={4} align="center" justify="space-between">
        {/* Left Section - Logo and Menu Toggle */}
        <HStack spacing={4}>
          <IconButton
            aria-label="Toggle sidebar"
            icon={<Icon>≡</Icon>}
            variant="ghost"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          />
          
          <Link href="/" passHref>
            <Flex align="center" cursor="pointer">
              <Flex
                w="32px"
                h="32px"
                bg="crypto.500"
                borderRadius="md"
                align="center"
                justify="center"
                color="white"
                fontWeight="bold"
                fontSize="lg"
              >
                O
              </Flex>
              <Text ml={2} fontSize="lg" fontWeight="bold" color={textColor}>
                Onchain Command Center
              </Text>
            </Flex>
          </Link>
        </HStack>

        {/* Center Section - Search */}
        <Box flex={1} maxW="600px" mx={8}>
          <form onSubmit={handleSearch}>
            <InputGroup>
              <InputLeftElement>
                <Icon color="gray.400">⌕</Icon>
              </InputLeftElement>
              <Input
                placeholder="Search entities, transactions, or addresses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                bg={useColorModeValue('gray.50', 'dark.700')}
                borderColor={useColorModeValue('gray.200', 'dark.600')}
                _focus={{
                  borderColor: 'crypto.500',
                  boxShadow: '0 0 0 1px var(--chakra-colors-crypto-500)',
                }}
              />
            </InputGroup>
          </form>
        </Box>

        {/* Right Section - Actions and User */}
        <HStack spacing={4}>
          {/* Notifications */}
          <Tooltip label="Notifications">
            <IconButton
              aria-label="Notifications"
              icon={<Icon>!</Icon>}
              variant="ghost"
              position="relative"
            >
              <Badge
                position="absolute"
                top={1}
                right={1}
                colorScheme="error"
                size="sm"
                borderRadius="full"
              >
                3
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Theme Toggle */}
          <Tooltip label={`Switch to ${colorMode === 'dark' ? 'light' : 'dark'} mode`}>
            <IconButton
              aria-label="Toggle color mode"
              icon={<Icon>{colorMode === 'dark' ? '☀' : '☾'}</Icon>}
              variant="ghost"
              onClick={toggleColorMode}
            />
          </Tooltip>

          {/* User Menu */}
          <Menu>
            <MenuButton as={Button} variant="ghost" px={2}>
              <HStack spacing={2}>
                <Avatar size="sm" name="User" bg="crypto.500" />
                <Text fontSize="sm" color={textColor}>
                  Analyst
                </Text>
              </HStack>
            </MenuButton>
            <MenuList bg={bg} borderColor={borderColor}>
              <MenuItem>Profile</MenuItem>
              <MenuItem>Settings</MenuItem>
              <Divider />
              <MenuItem>Sign Out</MenuItem>
            </MenuList>
          </Menu>
        </HStack>
      </Flex>

      {/* Sidebar Navigation */}
      {isSidebarOpen && (
        <Box
          position="fixed"
          left={0}
          top="60px"
          bottom={0}
          w="280px"
          bg={bg}
          borderRight="1px solid"
          borderColor={borderColor}
          overflowY="auto"
          zIndex={999}
        >
          <VStack spacing={0} align="stretch" py={4}>
            {navItems.map((item) => (
              <Box key={item.href}>
                <Link href={item.href} passHref>
                  <Flex
                    px={4}
                    py={3}
                    align="center"
                    cursor="pointer"
                    bg={isActive(item.href) ? 'crypto.500' : 'transparent'}
                    color={isActive(item.href) ? 'white' : textColor}
                    _hover={{
                      bg: isActive(item.href) ? 'crypto.600' : hoverBg,
                    }}
                    transition="all 0.2s"
                  >
                    <Icon mr={3} fontSize="lg">
                      {item.icon}
                    </Icon>
                    <Text flex={1} fontWeight="medium">
                      {item.label}
                    </Text>
                    {item.badge && (
                      <Badge colorScheme="crypto" size="sm">
                        {item.badge}
                      </Badge>
                    )}
                  </Flex>
                </Link>

                {/* Submenu */}
                {item.children && isActive(item.href) && (
                  <VStack spacing={0} align="stretch" ml={8}>
                    {item.children.map((child) => (
                      <Link key={child.href} href={child.href} passHref>
                        <Flex
                          px={4}
                          py={2}
                          align="center"
                          cursor="pointer"
                          bg={isActive(child.href) ? 'crypto.100' : 'transparent'}
                          color={isActive(child.href) ? 'crypto.700' : 'gray.500'}
                          _hover={{
                            bg: isActive(child.href) ? 'crypto.200' : 'gray.100',
                          }}
                          transition="all 0.2s"
                        >
                          <Icon mr={3} fontSize="md">
                            {child.icon}
                          </Icon>
                          <Text fontSize="sm">{child.label}</Text>
                        </Flex>
                      </Link>
                    ))}
                  </VStack>
                )}
              </Box>
            ))}
          </VStack>

          {/* Bottom Section */}
          <Box position="absolute" bottom={0} left={0} right={0} p={4} borderTop="1px solid" borderColor={borderColor}>
            <VStack spacing={2} align="stretch">
              <Text fontSize="xs" color="gray.500" textAlign="center">
                System Status
              </Text>
              <HStack justify="space-between">
                <Text fontSize="xs" color="success.500">
                  All Systems Operational
                </Text>
                <Badge colorScheme="success" size="sm">
                  ONLINE
                </Badge>
              </HStack>
            </VStack>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default PalantirNav; 