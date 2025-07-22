import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Collapse,
  Divider,
  Badge,
  Tooltip,
  useColorModeValue,
} from '@chakra-ui/react';
import { Button } from '../atoms/Button';
import { Icon, IconType } from '../atoms/Icon';
import { colors } from '../../theme/colors';
import { textStyles } from '../../theme/typography';
import { transitionPresets } from '../../theme/motion';

interface SideBarItem {
  id: string;
  label: string;
  icon: IconType;
  href?: string;
  count?: number;
  isActive?: boolean;
  isCollapsible?: boolean;
  children?: SideBarItem[];
  badge?: {
    text: string;
    color: string;
  };
}

interface SideBarProps {
  items: SideBarItem[];
  isCollapsed?: boolean;
  width?: string | number;
  onItemClick?: (item: SideBarItem) => void;
  onToggleCollapse?: () => void;
  logo?: React.ReactNode;
  footer?: React.ReactNode;
}

interface SideBarItemProps {
  item: SideBarItem;
  level?: number;
  isCollapsed?: boolean;
  onItemClick?: (item: SideBarItem) => void;
}

const SideBarItemComponent: React.FC<SideBarItemProps> = ({
  item,
  level = 0,
  isCollapsed = false,
  onItemClick,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const hasChildren = item.children && item.children.length > 0;
  
  const handleClick = () => {
    if (hasChildren && item.isCollapsible) {
      setIsExpanded(!isExpanded);
    }
    
    if (onItemClick) {
      onItemClick(item);
    }
  };

  const itemBg = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const activeBg = useColorModeValue(colors.primary[50], colors.primary[900]);
  const activeColor = colors.primary[600];

  return (
    <Box>
      <Tooltip
        label={isCollapsed ? item.label : ''}
        placement="right"
        isDisabled={!isCollapsed}
      >
        <Button
          variant="ghost"
          size="sm"
          width="100%"
          justifyContent="flex-start"
          px={3}
          py={2}
          h="auto"
          minH="40px"
          bg={item.isActive ? activeBg : itemBg}
          color={item.isActive ? activeColor : 'inherit'}
          borderRadius="md"
          transition={transitionPresets.hover}
          _hover={{
            bg: item.isActive ? activeBg : hoverBg,
            transform: 'translateX(2px)',
          }}
          onClick={handleClick}
          fontWeight={item.isActive ? 'semibold' : 'normal'}
          pl={level * 4 + 3}
        >
          <HStack width="100%" spacing={3}>
            <Icon name={item.icon} size="sm" />
            
            {!isCollapsed && (
              <>
                <Text flex="1" textAlign="left" {...textStyles.body}>
                  {item.label}
                </Text>
                
                {item.count !== undefined && item.count > 0 && (
                  <Badge
                    colorScheme={item.isActive ? 'blue' : 'gray'}
                    borderRadius="full"
                    fontSize="xs"
                  >
                    {item.count}
                  </Badge>
                )}
                
                {item.badge && (
                  <Badge
                    colorScheme={item.badge.color}
                    borderRadius="full"
                    fontSize="xs"
                  >
                    {item.badge.text}
                  </Badge>
                )}
                
                {hasChildren && item.isCollapsible && (
                  <Icon
                    name={isExpanded ? 'chevron-down' : 'chevron-right'}
                    size="xs"
                    transition={transitionPresets.hover}
                  />
                )}
              </>
            )}
          </HStack>
        </Button>
      </Tooltip>

      {/* Render children */}
      {hasChildren && !isCollapsed && (
        <Collapse in={isExpanded} animateOpacity>
          <VStack spacing={1} align="stretch" mt={1}>
            {item.children!.map((child) => (
              <SideBarItemComponent
                key={child.id}
                item={child}
                level={level + 1}
                isCollapsed={isCollapsed}
                onItemClick={onItemClick}
              />
            ))}
          </VStack>
        </Collapse>
      )}
    </Box>
  );
};

export const SideBar: React.FC<SideBarProps> = ({
  items,
  isCollapsed = false,
  width = isCollapsed ? '60px' : '280px',
  onItemClick,
  onToggleCollapse,
  logo,
  footer,
}) => {
  const bgColor = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  return (
    <Box
      width={width}
      height="100vh"
      bg={bgColor}
      borderRight="1px solid"
      borderColor={borderColor}
      transition={transitionPresets.panel}
      position="sticky"
      top={0}
      zIndex={10}
    >
      <VStack spacing={0} height="100%">
        {/* Header */}
        <Box width="100%" p={4}>
          <HStack justify="space-between">
            {logo && !isCollapsed && logo}
            
            <Tooltip label={isCollapsed ? 'Expand' : 'Collapse'} placement="right">
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleCollapse}
                _hover={{
                  bg: useColorModeValue('gray.100', 'gray.700'),
                }}
              >
                <Icon name={isCollapsed ? 'chevron-right' : 'chevron-left'} size="sm" />
              </Button>
            </Tooltip>
          </HStack>
          
          {!isCollapsed && (
            <Text
              mt={2}
              fontSize="xs"
              color="gray.500"
              fontWeight="semibold"
              textTransform="uppercase"
              letterSpacing="wide"
            >
              Navigation
            </Text>
          )}
        </Box>

        <Divider />

        {/* Navigation Items */}
        <Box flex="1" width="100%" px={3} py={4} overflowY="auto">
          <VStack spacing={1} align="stretch">
            {items.map((item) => (
              <SideBarItemComponent
                key={item.id}
                item={item}
                isCollapsed={isCollapsed}
                onItemClick={onItemClick}
              />
            ))}
          </VStack>
        </Box>

        {/* Footer */}
        {footer && (
          <>
            <Divider />
            <Box width="100%" p={4}>
              {footer}
            </Box>
          </>
        )}
      </VStack>
    </Box>
  );
};

// Quick action panel for common blockchain operations
interface QuickActionProps {
  onAddressLookup?: () => void;
  onTransactionTrace?: () => void;
  onContractAnalysis?: () => void;
  onRiskAssessment?: () => void;
  isCollapsed?: boolean;
}

export const QuickActionPanel: React.FC<QuickActionProps> = ({
  onAddressLookup,
  onTransactionTrace,
  onContractAnalysis,
  onRiskAssessment,
  isCollapsed = false,
}) => {
  const actions = [
    {
      icon: 'search' as IconType,
      label: 'Address Lookup',
      color: colors.primary[600],
      onClick: onAddressLookup,
    },
    {
      icon: 'transaction' as IconType,
      label: 'Trace Transaction',
      color: colors.info,
      onClick: onTransactionTrace,
    },
    {
      icon: 'contract' as IconType,
      label: 'Analyze Contract',
      color: colors.warning,
      onClick: onContractAnalysis,
    },
    {
      icon: 'shield' as IconType,
      label: 'Risk Assessment',
      color: colors.error,
      onClick: onRiskAssessment,
    },
  ];

  return (
    <Box width="100%">
      {!isCollapsed && (
        <Text
          fontSize="xs"
          color="gray.500"
          fontWeight="semibold"
          textTransform="uppercase"
          letterSpacing="wide"
          mb={3}
        >
          Quick Actions
        </Text>
      )}
      
      <VStack spacing={2}>
        {actions.map((action, index) => (
          <Tooltip
            key={index}
            label={isCollapsed ? action.label : ''}
            placement="right"
            isDisabled={!isCollapsed}
          >
            <Button
              variant="ghost"
              size="sm"
              width="100%"
              justifyContent={isCollapsed ? 'center' : 'flex-start'}
              onClick={action.onClick}
              leftIcon={<Icon name={action.icon} color={action.color} />}
              _hover={{
                bg: useColorModeValue('gray.50', 'gray.700'),
                transform: 'translateX(2px)',
              }}
            >
              {!isCollapsed && action.label}
            </Button>
          </Tooltip>
        ))}
      </VStack>
    </Box>
  );
};

// Status panel showing system health
interface StatusPanelProps {
  networkStatus?: 'connected' | 'disconnected' | 'syncing';
  dataFreshness?: string;
  activeConnections?: number;
  isCollapsed?: boolean;
}

export const StatusPanel: React.FC<StatusPanelProps> = ({
  networkStatus = 'connected',
  dataFreshness = 'Live',
  activeConnections = 0,
  isCollapsed = false,
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return colors.success;
      case 'syncing':
        return colors.warning;
      case 'disconnected':
        return colors.error;
      default:
        return colors.gray[500];
    }
  };

  if (isCollapsed) {
    return (
      <VStack spacing={2}>
        <Tooltip label={`Network: ${networkStatus}`} placement="right">
          <Box
            width="8px"
            height="8px"
            borderRadius="50%"
            bg={getStatusColor(networkStatus)}
          />
        </Tooltip>
      </VStack>
    );
  }

  return (
    <VStack spacing={2} align="stretch">
      <Text
        fontSize="xs"
        color="gray.500"
        fontWeight="semibold"
        textTransform="uppercase"
        letterSpacing="wide"
      >
        System Status
      </Text>
      
      <HStack justify="space-between">
        <Text fontSize="xs" color="gray.600">
          Network
        </Text>
        <HStack spacing={1}>
          <Box
            width="6px"
            height="6px"
            borderRadius="50%"
            bg={getStatusColor(networkStatus)}
          />
          <Text fontSize="xs" fontWeight="medium" color={getStatusColor(networkStatus)}>
            {networkStatus}
          </Text>
        </HStack>
      </HStack>
      
      <HStack justify="space-between">
        <Text fontSize="xs" color="gray.600">
          Data
        </Text>
        <Text fontSize="xs" fontWeight="medium">
          {dataFreshness}
        </Text>
      </HStack>
      
      <HStack justify="space-between">
        <Text fontSize="xs" color="gray.600">
          Connections
        </Text>
        <Text fontSize="xs" fontWeight="medium">
          {activeConnections}
        </Text>
      </HStack>
    </VStack>
  );
};

export default SideBar;
