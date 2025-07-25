/**
 * Enhanced Top Navigation Bar
 * Ultra-thin 48px height with Palantir + ChatGPT + Apple aesthetics
 */

import React, { useState } from 'react';
import {
  Box,
  HStack,
  Text,
  IconButton,
  Input,
  InputGroup,
  InputLeftElement,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Badge,
  Tooltip,
  useColorMode,
  Kbd,
} from '@chakra-ui/react';
import {
  SearchIcon,
  BellIcon,
  SettingsIcon,
  MoonIcon,
  SunIcon,
  HamburgerIcon,
} from '@chakra-ui/icons';
import { motion } from 'framer-motion';
import * as Cmdk from 'cmdk';
import { useHotkeys } from 'react-hotkeys-hook';
import { useRouter } from 'next/router';
import { AnimatePresence } from 'framer-motion';

const MotionBox = motion(Box);
const MotionHStack = motion(HStack);

interface TopNavProps {
  onSidebarToggle: () => void;
  isSidebarOpen: boolean;
}

const TopNav: React.FC<TopNavProps> = ({ onSidebarToggle, isSidebarOpen }) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const [searchFocused, setSearchFocused] = useState(false);
  const [omniboxOpen, setOmniboxOpen] = useState(false);
  const [omniboxQuery, setOmniboxQuery] = useState('');
  const router = useRouter();

  useHotkeys('meta+k,ctrl+k', () => setOmniboxOpen(true), []);

  const NAV_ITEMS = [
    { label: 'Dashboard', path: '/' },
    { label: 'Services', path: '/services' },
    { label: 'Graph API', path: '/services/graph' },
    { label: 'Voice Ops', path: '/voice' },
    { label: 'Ingestion', path: '/ingestion' },
    { label: 'Architecture', path: '/architecture' },
    { label: 'Graph Explorer', path: '/explorer' },
    { label: 'Time Canvas', path: '/canvas' },
    { label: 'Compliance', path: '/compliance' },
    { label: 'Workspace', path: '/workspace' },
    { label: 'Monitoring', path: '/monitoring' },
    { label: 'Analytics', path: '/analytics' },
    { label: 'Ontology', path: '/ontology' },
    { label: 'MEV', path: '/mev' },
    { label: 'Status', path: '/status' },
    { label: 'Signals', path: '/workflows/signals' },
    { label: 'Dagster', path: '/workflows/dagster' },
    { label: 'Entities', path: '/intelligence/entities' },
    { label: 'Access', path: '/security/access' },
    { label: 'API Gateway', path: '/api/gateway' },
  ];

  const filteredItems = NAV_ITEMS.filter(item =>
    item.label.toLowerCase().includes(omniboxQuery.toLowerCase())
  );

  return (
    <MotionBox
      as="header"
      height="48px"
      bg={colorMode === 'dark' ? 'palantir.navy' : 'white'}
      borderBottom="1px solid"
      borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.200'}
      backdropFilter="blur(10px)"
      position="sticky"
      top={0}
      zIndex={1000}
      initial={{ y: -48 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      <HStack height="100%" px={4} justify="space-between" spacing={4}>
        {/* Left Section */}
        <HStack spacing={4}>
          {/* Sidebar Toggle */}
          <Tooltip label={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}>
            <IconButton
              aria-label="Toggle sidebar"
              icon={<HamburgerIcon />}
              variant="ghost"
              size="sm"
              onClick={onSidebarToggle}
              _hover={{
                bg: colorMode === 'dark' ? 'palantir.navy-light' : 'gray.100',
              }}
            />
          </Tooltip>

          {/* Logo */}
          <MotionHStack
            spacing={2}
            whileHover={{ scale: 1.05 }}
            cursor="pointer"
          >
            <Box
              w="24px"
              h="24px"
              borderRadius="md"
              bg="linear-gradient(135deg, #14C8FF, #0958D9)"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Text fontSize="xs" fontWeight="bold" color="white">
                🕸️
              </Text>
            </Box>
            <Text
              fontSize="md"
              fontWeight="bold"
              color={colorMode === 'dark' ? 'white' : 'gray.900'}
              letterSpacing="tight"
            >
              Onchain Command Center
            </Text>
            <Badge
              size="sm"
              colorScheme="blue"
              variant="subtle"
              borderRadius="full"
            >
              v3
            </Badge>
          </MotionHStack>
        </HStack>

        {/* Center - Quick Search */}
        <Box maxW="400px" flex="1">
          <InputGroup size="sm">
            <InputLeftElement pointerEvents="none">
              <SearchIcon color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Quick search entities, addresses, transactions..."
              bg={colorMode === 'dark' ? 'palantir.navy-light' : 'gray.50'}
              border="1px solid"
              borderColor={searchFocused ? 'brand.500' : 'transparent'}
              _hover={{
                borderColor: colorMode === 'dark' ? 'gray.500' : 'gray.300',
              }}
              _focus={{
                borderColor: 'brand.500',
                boxShadow: '0 0 0 1px #14C8FF',
                bg: colorMode === 'dark' ? 'gray.800' : 'white',
              }}
              borderRadius="lg"
              fontSize="sm"
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
            />
          </InputGroup>
          {searchFocused && (
            <Box
              position="absolute"
              right={2}
              fontSize="xs"
              color="gray.400"
              display="flex"
              alignItems="center"
              gap={1}
            >
              <Kbd>⌘</Kbd>
              <Kbd>K</Kbd>
            </Box>
          )}
        </Box>

        {/* Right Section */}
        <HStack spacing={2}>
          {/* Notifications */}
          <Tooltip label="Notifications">
            <Box position="relative">
              <IconButton
                aria-label="Notifications"
                icon={<BellIcon />}
                variant="ghost"
                size="sm"
                _hover={{
                  bg: colorMode === 'dark' ? 'palantir.navy-light' : 'gray.100',
                }}
              />
              <Badge
                position="absolute"
                top="-1"
                right="-1"
                colorScheme="red"
                borderRadius="full"
                fontSize="xs"
                minW="16px"
                h="16px"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                3
              </Badge>
            </Box>
          </Tooltip>

          {/* Theme Toggle */}
          <Tooltip label={`Switch to ${colorMode === 'dark' ? 'light' : 'dark'} mode`}>
            <IconButton
              aria-label="Toggle theme"
              icon={colorMode === 'dark' ? <SunIcon /> : <MoonIcon />}
              variant="ghost"
              size="sm"
              onClick={toggleColorMode}
              _hover={{
                bg: colorMode === 'dark' ? 'palantir.navy-light' : 'gray.100',
                transform: 'rotate(180deg)',
              }}
              transition="all 0.3s ease"
            />
          </Tooltip>

          {/* Settings */}
          <Tooltip label="Settings">
            <IconButton
              aria-label="Settings"
              icon={<SettingsIcon />}
              variant="ghost"
              size="sm"
              _hover={{
                bg: colorMode === 'dark' ? 'palantir.navy-light' : 'gray.100',
                transform: 'rotate(90deg)',
              }}
              transition="all 0.3s ease"
            />
          </Tooltip>

          {/* Profile Menu */}
          <Menu>
            <MenuButton>
              <Avatar
                size="sm"
                name="Analyst"
                src="/avatar-placeholder.jpg"
                bg="brand.500"
                color="white"
                _hover={{
                  boxShadow: '0 0 20px rgba(20, 200, 255, 0.4)',
                }}
                transition="all 0.2s"
              />
            </MenuButton>
            <MenuList
              bg={colorMode === 'dark' ? 'palantir.navy-light' : 'white'}
              border="1px solid"
              borderColor={colorMode === 'dark' ? 'gray.600' : 'gray.200'}
              borderRadius="xl"
              boxShadow="xl"
            >
              <MenuItem>Profile Settings</MenuItem>
              <MenuItem>API Keys</MenuItem>
              <MenuItem>Workspace Settings</MenuItem>
              <MenuItem>Sign Out</MenuItem>
            </MenuList>
          </Menu>
        </HStack>
      </HStack>
      <AnimatePresence>
        {omniboxOpen && (
          <MotionBox
            position="fixed"
            top={0}
            left={0}
            w="100vw"
            h="100vh"
            bg="rgba(0,0,0,0.3)"
            zIndex={2000}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOmniboxOpen(false)}
          >
            <MotionBox
              as={Cmdk.Command}
              position="absolute"
              top="20vh"
              left="50%"
              transform="translateX(-50%)"
              w="400px"
              bg={colorMode === 'dark' ? 'gray.800' : 'white'}
              borderRadius="xl"
              boxShadow="2xl"
              p={4}
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
              <Cmdk.CommandInput
                autoFocus
                placeholder="Jump to..."
                value={omniboxQuery}
                onValueChange={setOmniboxQuery}
                style={{ width: '100%', padding: '8px', borderRadius: '8px', fontSize: '1rem', marginBottom: '8px' }}
              />
              <Cmdk.CommandList>
                {filteredItems.length === 0 && <Cmdk.CommandEmpty>No results found.</Cmdk.CommandEmpty>}
                {filteredItems.map(item => (
                  <Cmdk.CommandItem
                    key={item.path}
                    onSelect={() => {
                      setOmniboxOpen(false);
                      setOmniboxQuery('');
                      router.push(item.path);
                    }}
                    style={{ padding: '8px', borderRadius: '6px', cursor: 'pointer' }}
                  >
                    {item.label}
                  </Cmdk.CommandItem>
                ))}
              </Cmdk.CommandList>
            </MotionBox>
          </MotionBox>
        )}
      </AnimatePresence>
    </MotionBox>
  );
};

export default TopNav;
