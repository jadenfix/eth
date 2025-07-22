import React from 'react';
import {
  Box,
  HStack,
  VStack,
  Text,
  Flex,
  Spacer,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Tooltip,
  useColorModeValue,
} from '@chakra-ui/react';
import { Button } from '../atoms/Button';
import { Icon, IconType } from '../atoms/Icon';
import { colors } from '../../theme/colors';
import { textStyles } from '../../theme/typography';
import { transitionPresets } from '../../theme/motion';

interface PanelHeaderProps {
  title: string;
  subtitle?: string;
  icon?: IconType;
  badge?: {
    text: string;
    color?: 'gray' | 'red' | 'orange' | 'yellow' | 'green' | 'blue' | 'purple';
  };
  actions?: React.ReactNode;
  onClose?: () => void;
  onMinimize?: () => void;
  onMaximize?: () => void;
  isCollapsible?: boolean;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
  isResizable?: boolean;
  isDraggable?: boolean;
  dragHandle?: boolean;
}

interface ActionButtonProps {
  icon: IconType;
  tooltip: string;
  onClick?: () => void;
  color?: string;
  variant?: 'ghost' | 'primary';
  isDisabled?: boolean;
}

const ActionButton: React.FC<ActionButtonProps> = ({
  icon,
  tooltip,
  onClick,
  color = 'gray.500',
  variant = 'ghost',
  isDisabled = false,
}) => {
  return (
    <Tooltip label={tooltip} placement="bottom">
      <Button
        variant={variant}
        size="xs"
        p={1}
        minW="24px"
        h="24px"
        onClick={onClick}
        isDisabled={isDisabled}
        color={color}
        _hover={{
          bg: useColorModeValue('gray.100', 'gray.700'),
          color: color,
        }}
        _active={{
          bg: useColorModeValue('gray.200', 'gray.600'),
        }}
      >
        <Icon name={icon} size="xs" />
      </Button>
    </Tooltip>
  );
};

interface ContextMenuProps {
  onRefresh?: () => void;
  onExport?: () => void;
  onSettings?: () => void;
  onDuplicate?: () => void;
  onDelete?: () => void;
  customItems?: Array<{
    label: string;
    icon: IconType;
    onClick: () => void;
    isDivider?: boolean;
    color?: string;
  }>;
}

const ContextMenu: React.FC<ContextMenuProps> = ({
  onRefresh,
  onExport,
  onSettings,
  onDuplicate,
  onDelete,
  customItems = [],
}) => {
  return (
    <Menu>
      <MenuButton
        as={Button}
        variant="ghost"
        size="xs"
        p={1}
        minW="24px"
        h="24px"
        _hover={{
          bg: useColorModeValue('gray.100', 'gray.700'),
        }}
      >
        <Icon name="menu" size="xs" />
      </MenuButton>
      <MenuList fontSize="sm">
        {onRefresh && (
          <MenuItem onClick={onRefresh}>
            <Icon name="refresh" size="sm" mr={3} />
            Refresh
          </MenuItem>
        )}
        
        {onExport && (
          <MenuItem onClick={onExport}>
            <Icon name="download" size="sm" mr={3} />
            Export Data
          </MenuItem>
        )}
        
        {onDuplicate && (
          <MenuItem onClick={onDuplicate}>
            <Icon name="copy" size="sm" mr={3} />
            Duplicate Panel
          </MenuItem>
        )}

        {(onRefresh || onExport || onDuplicate) && (onSettings || onDelete || customItems.length > 0) && (
          <MenuDivider />
        )}

        {customItems.map((item, index) => (
          <React.Fragment key={index}>
            {item.isDivider ? (
              <MenuDivider />
            ) : (
              <MenuItem onClick={item.onClick} color={item.color}>
                <Icon name={item.icon} size="sm" mr={3} />
                {item.label}
              </MenuItem>
            )}
          </React.Fragment>
        ))}

        {onSettings && (
          <MenuItem onClick={onSettings}>
            <Icon name="settings" size="sm" mr={3} />
            Settings
          </MenuItem>
        )}

        {onDelete && (
          <>
            {onSettings && <MenuDivider />}
            <MenuItem onClick={onDelete} color="red.500">
              <Icon name="close" size="sm" mr={3} />
              Remove Panel
            </MenuItem>
          </>
        )}
      </MenuList>
    </Menu>
  );
};

export const PanelHeader: React.FC<PanelHeaderProps> = ({
  title,
  subtitle,
  icon,
  badge,
  actions,
  onClose,
  onMinimize,
  onMaximize,
  isCollapsible = false,
  isCollapsed = false,
  onToggleCollapse,
  isResizable = false,
  isDraggable = false,
  dragHandle = false,
}) => {
  const bgColor = useColorModeValue('gray.50', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box
      bg={bgColor}
      borderBottom="1px solid"
      borderColor={borderColor}
      px={4}
      py={3}
      cursor={isDraggable && dragHandle ? 'move' : 'default'}
      userSelect={isDraggable && dragHandle ? 'none' : 'auto'}
      transition={transitionPresets.hover}
      _hover={isDraggable && dragHandle ? {
        bg: useColorModeValue('gray.100', 'gray.700'),
      } : undefined}
    >
      <Flex align="center">
        {/* Icon and Title */}
        <HStack spacing={3} flex="1" minW={0}>
          {icon && (
            <Icon
              name={icon}
              size="md"
              color={colors.primary[600]}
            />
          )}
          
          <VStack spacing={0} align="start" flex="1" minW={0}>
            <HStack spacing={2}>
              <Text
                color={useColorModeValue('gray.800', 'gray.200')}
                noOfLines={1}
                {...textStyles.h3}
              >
                {title}
              </Text>
              
              {badge && (
                <Badge
                  colorScheme={badge.color || 'gray'}
                  fontSize="xs"
                  borderRadius="full"
                >
                  {badge.text}
                </Badge>
              )}
            </HStack>
            
            {subtitle && !isCollapsed && (
              <Text
                color="gray.500"
                noOfLines={1}
                {...textStyles.caption}
              >
                {subtitle}
              </Text>
            )}
          </VStack>
        </HStack>

        <Spacer />

        {/* Custom Actions */}
        {actions && !isCollapsed && (
          <Box mr={2}>
            {actions}
          </Box>
        )}

        {/* Control Actions */}
        <HStack spacing={1}>
          {isCollapsible && (
            <ActionButton
              icon={isCollapsed ? 'expand' : 'collapse'}
              tooltip={isCollapsed ? 'Expand Panel' : 'Collapse Panel'}
              onClick={onToggleCollapse}
            />
          )}

          {onMinimize && (
            <ActionButton
              icon="minus"
              tooltip="Minimize Panel"
              onClick={onMinimize}
            />
          )}

          {onMaximize && (
            <ActionButton
              icon="expand"
              tooltip="Maximize Panel"
              onClick={onMaximize}
            />
          )}

          {onClose && (
            <ActionButton
              icon="close"
              tooltip="Close Panel"
              onClick={onClose}
              color="red.500"
            />
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

// Specialized header for data tables
interface TableHeaderProps {
  title: string;
  totalCount?: number;
  filteredCount?: number;
  isLoading?: boolean;
  onRefresh?: () => void;
  onExport?: () => void;
  onFilter?: () => void;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  actions?: React.ReactNode;
}

export const TableHeader: React.FC<TableHeaderProps> = ({
  title,
  totalCount,
  filteredCount,
  isLoading = false,
  onRefresh,
  onExport,
  onFilter,
  searchValue = '',
  onSearchChange,
  actions,
}) => {
  const getCountDisplay = () => {
    if (totalCount === undefined) return '';
    if (filteredCount !== undefined && filteredCount !== totalCount) {
      return `${filteredCount} of ${totalCount}`;
    }
    return totalCount.toLocaleString();
  };

  return (
    <PanelHeader
      title={title}
      subtitle={getCountDisplay()}
      icon="table"
      actions={
        <HStack spacing={2}>
          {/* Search Input */}
          {onSearchChange && (
            <Box position="relative">
              <Box
                as="input"
                placeholder="Search..."
                value={searchValue}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => onSearchChange(e.target.value)}
                px={3}
                py={1}
                pr={8}
                fontSize="sm"
                bg={useColorModeValue('white', 'gray.700')}
                border="1px solid"
                borderColor={useColorModeValue('gray.300', 'gray.600')}
                borderRadius="md"
                _focus={{
                  borderColor: colors.primary[400],
                  outline: 'none',
                }}
                w="200px"
              />
              <Icon
                name="search"
                size="xs"
                position="absolute"
                right="8px"
                top="50%"
                transform="translateY(-50%)"
                color="gray.400"
              />
            </Box>
          )}

          {onFilter && (
            <ActionButton
              icon="filter"
              tooltip="Filter Results"
              onClick={onFilter}
            />
          )}

          {onRefresh && (
            <ActionButton
              icon="refresh"
              tooltip="Refresh Data"
              onClick={onRefresh}
              isDisabled={isLoading}
            />
          )}

          {onExport && (
            <ActionButton
              icon="download"
              tooltip="Export Data"
              onClick={onExport}
            />
          )}

          {actions}
        </HStack>
      }
    />
  );
};

// Chart/Graph header with time controls
interface ChartHeaderProps {
  title: string;
  timeRange?: string;
  onTimeRangeChange?: (range: string) => void;
  isLoading?: boolean;
  onRefresh?: () => void;
  onFullscreen?: () => void;
  metrics?: Array<{
    label: string;
    value: string;
    color?: string;
  }>;
}

export const ChartHeader: React.FC<ChartHeaderProps> = ({
  title,
  timeRange = '24h',
  onTimeRangeChange,
  isLoading = false,
  onRefresh,
  onFullscreen,
  metrics = [],
}) => {
  const timeRanges = ['1h', '6h', '24h', '7d', '30d', '90d'];

  return (
    <PanelHeader
      title={title}
      icon="chart"
      actions={
        <HStack spacing={3}>
          {/* Metrics */}
          {metrics.length > 0 && (
            <HStack spacing={4}>
              {metrics.map((metric, index) => (
                <VStack key={index} spacing={0} align="center">
                  <Text fontSize="xs" color="gray.500">
                    {metric.label}
                  </Text>
                  <Text fontSize="sm" fontWeight="semibold" color={metric.color}>
                    {metric.value}
                  </Text>
                </VStack>
              ))}
            </HStack>
          )}

          {/* Time Range Selector */}
          {onTimeRangeChange && (
            <HStack spacing={1} bg={useColorModeValue('white', 'gray.700')} p={1} borderRadius="md">
              {timeRanges.map((range) => (
                <Button
                  key={range}
                  size="xs"
                  variant={timeRange === range ? 'primary' : 'ghost'}
                  onClick={() => onTimeRangeChange(range)}
                  minW="32px"
                >
                  {range}
                </Button>
              ))}
            </HStack>
          )}

          {onRefresh && (
            <ActionButton
              icon="refresh"
              tooltip="Refresh Chart"
              onClick={onRefresh}
              isDisabled={isLoading}
            />
          )}

          {onFullscreen && (
            <ActionButton
              icon="expand"
              tooltip="Fullscreen"
              onClick={onFullscreen}
            />
          )}
        </HStack>
      }
    />
  );
};

export default PanelHeader;
