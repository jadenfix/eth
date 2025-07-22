import React from 'react';
import {
  Box,
  Flex,
  HStack,
  VStack,
  Text,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Avatar,
  Spacer,
  useColorModeValue,
  Tooltip,
} from '@chakra-ui/react';
import { Button } from '../atoms/Button';
import { Icon } from '../atoms/Icon';
import { Spinner } from '../atoms/Spinner';
import { colors } from '../../theme/colors';
import { textStyles } from '../../theme/typography';
import { transitionPresets } from '../../theme/motion';

interface NavBarProps {
  user?: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  notifications?: number;
  isLoading?: boolean;
  onSearch?: (query: string) => void;
  onNotificationsClick?: () => void;
  onSettingsClick?: () => void;
  onLogout?: () => void;
  children?: React.ReactNode;
}

interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  isLoading?: boolean;
}

const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Search addresses, transactions, contracts...',
  onSearch,
  isLoading = false,
}) => {
  const [query, setQuery] = React.useState('');
  const [isFocused, setIsFocused] = React.useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && onSearch) {
      onSearch(query.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e as any);
    }
  };

  return (
    <Box position="relative" flex="1" maxW="600px">
      <form onSubmit={handleSubmit}>
        <Flex
          align="center"
          bg={useColorModeValue('white', 'gray.800')}
          border="1px solid"
          borderColor={isFocused ? colors.primary[400] : 'gray.200'}
          borderRadius="lg"
          px={4}
          py={2}
          transition={transitionPresets.hover}
          _hover={{
            borderColor: colors.primary[300],
          }}
        >
          <Icon name="search" size="sm" color="gray.400" />
          <Box
            as="input"
            flex="1"
            ml={3}
            placeholder={placeholder}
            value={query}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            onKeyDown={handleKeyDown}
            border="none"
            outline="none"
            fontSize="sm"
            color={useColorModeValue('gray.700', 'gray.200')}
            _placeholder={{ color: 'gray.400' }}
          />
          {isLoading && <Spinner size="sm" />}
        </Flex>
      </form>
      
      {/* Search suggestions could go here */}
      {isFocused && query && (
        <Box
          position="absolute"
          top="100%"
          left={0}
          right={0}
          mt={1}
          bg={useColorModeValue('white', 'gray.800')}
          border="1px solid"
          borderColor="gray.200"
          borderRadius="lg"
          shadow="lg"
          zIndex={20}
          p={2}
        >
          <Text fontSize="xs" color="gray.500" p={2}>
            Press Enter to search
          </Text>
        </Box>
      )}
    </Box>
  );
};

interface NotificationBellProps {
  count?: number;
  onClick?: () => void;
}

const NotificationBell: React.FC<NotificationBellProps> = ({ count = 0, onClick }) => {
  return (
    <Tooltip label="Notifications">
      <Button
        variant="ghost"
        size="sm"
        position="relative"
        onClick={onClick}
        _hover={{
          bg: useColorModeValue('gray.100', 'gray.700'),
        }}
      >
        <Icon name="bell" size="md" />
        {count > 0 && (
          <Badge
            position="absolute"
            top="-2px"
            right="-2px"
            colorScheme="red"
            borderRadius="full"
            fontSize="xs"
            minW="18px"
            h="18px"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            {count > 99 ? '99+' : count}
          </Badge>
        )}
      </Button>
    </Tooltip>
  );
};

interface UserMenuProps {
  user: {
    name: string;
    email: string;
    avatar?: string;
    role?: string;
  };
  onSettingsClick?: () => void;
  onLogout?: () => void;
}

const UserMenu: React.FC<UserMenuProps> = ({ user, onSettingsClick, onLogout }) => {
  return (
    <Menu>
      <MenuButton
        as={Button}
        variant="ghost"
        size="sm"
        p={1}
        _hover={{
          bg: useColorModeValue('gray.100', 'gray.700'),
        }}
      >
        <HStack spacing={2}>
          <Avatar size="sm" name={user.name} src={user.avatar} />
          <VStack spacing={0} align="start" display={{ base: 'none', md: 'flex' }}>
            <Text fontSize="sm" fontWeight="medium" lineHeight="1">
              {user.name}
            </Text>
            {user.role && (
              <Text fontSize="xs" color="gray.500" lineHeight="1">
                {user.role}
              </Text>
            )}
          </VStack>
          <Icon name="chevron-down" size="xs" />
        </HStack>
      </MenuButton>
      <MenuList>
        <MenuItem>
          <Icon name="user" size="sm" mr={3} />
          Profile
        </MenuItem>
        <MenuItem onClick={onSettingsClick}>
          <Icon name="settings" size="sm" mr={3} />
          Settings
        </MenuItem>
        <MenuDivider />
        <MenuItem color="red.500" onClick={onLogout}>
          <Icon name="logout" size="sm" mr={3} />
          Sign out
        </MenuItem>
      </MenuList>
    </Menu>
  );
};

export const NavBar: React.FC<NavBarProps> = ({
  user,
  notifications = 0,
  isLoading = false,
  onSearch,
  onNotificationsClick,
  onSettingsClick,
  onLogout,
  children,
}) => {
  return (
    <Box
      bg={useColorModeValue('white', 'gray.900')}
      borderBottom="1px solid"
      borderColor={useColorModeValue('gray.200', 'gray.700')}
      px={6}
      py={3}
      position="sticky"
      top={0}
      zIndex={100}
      backdropFilter="blur(10px)"
    >
      <Flex align="center" justify="space-between">
        {/* Logo/Brand */}
        <HStack spacing={4}>
          <Box>
            <Text
              color={colors.primary[600]}
              {...textStyles.h2}
            >
              Palantir Intelligence
            </Text>
            <Text fontSize="xs" color="gray.500">
              Blockchain Analysis Platform
            </Text>
          </Box>
        </HStack>

        {/* Search Bar */}
        <SearchBar
          onSearch={onSearch}
          isLoading={isLoading}
        />

        <Spacer />

        {/* Right Side Actions */}
        <HStack spacing={2}>
          {children}
          
          {/* Notifications */}
          <NotificationBell 
            count={notifications} 
            onClick={onNotificationsClick} 
          />

          {/* Settings */}
          <Tooltip label="Settings">
            <Button
              variant="ghost"
              size="sm"
              onClick={onSettingsClick}
              _hover={{
                bg: useColorModeValue('gray.100', 'gray.700'),
              }}
            >
              <Icon name="settings" size="md" />
            </Button>
          </Tooltip>

          {/* User Menu */}
          {user && (
            <UserMenu
              user={user}
              onSettingsClick={onSettingsClick}
              onLogout={onLogout}
            />
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

// Breadcrumb component for navigation context
interface BreadcrumbProps {
  items: Array<{
    label: string;
    href?: string;
    isCurrentPage?: boolean;
  }>;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <HStack
      spacing={2}
      fontSize="sm"
      color="gray.600"
      py={2}
      px={6}
      bg={useColorModeValue('gray.50', 'gray.800')}
      borderBottom="1px solid"
      borderColor={useColorModeValue('gray.200', 'gray.700')}
    >
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <Text
            color={item.isCurrentPage ? colors.primary[600] : 'gray.600'}
            fontWeight={item.isCurrentPage ? 'medium' : 'normal'}
            cursor={item.href && !item.isCurrentPage ? 'pointer' : 'default'}
            _hover={item.href && !item.isCurrentPage ? {
              color: colors.primary[600],
              textDecoration: 'underline',
            } : undefined}
          >
            {item.label}
          </Text>
          {index < items.length - 1 && (
            <Icon name="chevron-right" size="xs" color="gray.400" />
          )}
        </React.Fragment>
      ))}
    </HStack>
  );
};

export default NavBar;
