import React from 'react';
import { Icon as ChakraIcon, IconProps as ChakraIconProps } from '@chakra-ui/react';
import { colors } from '../../theme/colors';

// Common icon types used in blockchain intelligence
export type IconType = 
  | 'search' 
  | 'filter' 
  | 'sort' 
  | 'download' 
  | 'upload'
  | 'settings' 
  | 'info' 
  | 'warning' 
  | 'error' 
  | 'success'
  | 'close' 
  | 'menu' 
  | 'expand' 
  | 'collapse'
  | 'play' 
  | 'pause' 
  | 'stop' 
  | 'refresh'
  | 'copy' 
  | 'link' 
  | 'external' 
  | 'share'
  | 'user' 
  | 'wallet' 
  | 'transaction' 
  | 'block'
  | 'contract' 
  | 'token' 
  | 'graph' 
  | 'chart'
  | 'table' 
  | 'grid' 
  | 'list' 
  | 'timeline'
  | 'flag' 
  | 'shield' 
  | 'lock' 
  | 'unlock'
  | 'eye' 
  | 'eye-off' 
  | 'arrow-up' 
  | 'arrow-down'
  | 'arrow-left' 
  | 'arrow-right' 
  | 'chevron-up' 
  | 'chevron-down'
  | 'chevron-left' 
  | 'chevron-right' 
  | 'plus' 
  | 'minus'
  | 'check' 
  | 'star' 
  | 'bookmark' 
  | 'tag'
  | 'bell'
  | 'logout';

interface IconProps extends Omit<ChakraIconProps, 'children'> {
  name: IconType;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  color?: string;
  variant?: 'solid' | 'outline' | 'ghost';
}

// SVG path definitions for common icons
const iconPaths: Record<IconType, string> = {
  search: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z",
  filter: "M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z",
  sort: "M3 4h6M3 8h6m-6 4h6m-6 4h6M13 4l3 3m0 0l3-3m-3 3v12",
  download: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4",
  upload: "M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12",
  settings: "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
  info: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  warning: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z",
  error: "M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z",
  success: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  close: "M6 18L18 6M6 6l12 12",
  menu: "M4 6h16M4 12h16M4 18h16",
  expand: "M3 8l7.89 7.89a1 1 0 001.42 0L21 8M5 21V10a1 1 0 011-1h12a1 1 0 011 1v11",
  collapse: "M21 16l-7.89-7.89a1 1 0 00-1.42 0L3 16M19 3v11a1 1 0 01-1 1H8a1 1 0 01-1-1V3",
  play: "M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  pause: "M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z",
  stop: "M21 12a9 9 0 11-18 0 9 9 0 0118 0z M9 10h6v4H9z",
  refresh: "M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15",
  copy: "M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3",
  link: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1",
  external: "M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14",
  share: "M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z",
  user: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
  wallet: "M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z",
  transaction: "M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4",
  block: "M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547A1.993 1.993 0 004 17.5l5.5 5.5c.667.667 1.5.5 2 0L17 17.5c0-.75-.333-1.429-.572-2.072z",
  contract: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  token: "M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  graph: "M7 8l-4 4 4 4m6-8l4 4-4 4M11 6L9 18",
  chart: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
  table: "M3 10h18M3 14h18m-9-4v8m-7 0V4a1 1 0 011-1h16a1 1 0 011 1v16a1 1 0 01-1 1H5a1 1 0 01-1-1V4z",
  grid: "M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z",
  list: "M4 6h16M4 10h16M4 14h16M4 18h16",
  timeline: "M4 7v10c0 2.21 3.79 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.79 4 8 4s8-1.79 8-4M4 7c0-2.21 3.79-4 8-4s8 1.79 8 4m0 5c0 2.21-3.79 4-8 4s-8-1.79-8-4",
  flag: "M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 2h7a2 2 0 012 2v6a2 2 0 01-2 2H12l-1-2H5a2 2 0 00-2 2z",
  shield: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
  lock: "M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z",
  unlock: "M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z",
  eye: "M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z",
  "eye-off": "M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21",
  "arrow-up": "M7 14l5-5 5 5",
  "arrow-down": "M17 10l-5 5-5-5",
  "arrow-left": "M14 7l-5 5 5 5",
  "arrow-right": "M10 17l5-5-5-5",
  "chevron-up": "M5 15l7-7 7 7",
  "chevron-down": "M19 9l-7 7-7-7",
  "chevron-left": "M15 19l-7-7 7-7",
  "chevron-right": "M9 5l7 7-7 7",
  plus: "M12 4v16m8-8H4",
  minus: "M20 12H4",
  check: "M5 13l4 4L19 7",
  star: "M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z",
  bookmark: "M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z",
  tag: "M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z",
  bell: "M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9",
  logout: "M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1",
};

const getSizeValue = (size: IconProps['size']): number => {
  if (typeof size === 'number') return size;
  
  const sizeMap = {
    xs: 12,
    sm: 16,
    md: 20,
    lg: 24,
    xl: 32,
  };
  
  return sizeMap[size || 'md'];
};

export const Icon: React.FC<IconProps> = ({
  name,
  size = 'md',
  color = 'currentColor',
  variant = 'solid',
  ...props
}) => {
  const sizeValue = getSizeValue(size);
  const path = iconPaths[name];

  if (!path) {
    console.warn(`Icon "${name}" not found`);
    return null;
  }

  return (
    <ChakraIcon
      viewBox="0 0 24 24"
      boxSize={sizeValue}
      fill={variant === 'solid' ? color : 'none'}
      stroke={variant === 'outline' ? color : 'none'}
      strokeWidth={variant === 'outline' ? 2 : 0}
      strokeLinecap="round"
      strokeLinejoin="round"
      color={color}
      {...props}
    >
      <path d={path} />
    </ChakraIcon>
  );
};

// Status icon variants with predefined colors
export const StatusIcon: React.FC<Omit<IconProps, 'name' | 'color'> & { status: 'success' | 'warning' | 'error' | 'info' }> = ({
  status,
  ...props
}) => {
  const statusConfig = {
    success: { name: 'success' as IconType, color: colors.success },
    warning: { name: 'warning' as IconType, color: colors.warning },
    error: { name: 'error' as IconType, color: colors.error },
    info: { name: 'info' as IconType, color: colors.info },
  };

  const config = statusConfig[status];
  
  return <Icon name={config.name} color={config.color} {...props} />;
};

// Risk level icon with appropriate color
export const RiskIcon: React.FC<Omit<IconProps, 'name' | 'color'> & { level: 'low' | 'medium' | 'high' | 'critical' }> = ({
  level,
  ...props
}) => {
  const riskConfig = {
    low: { name: 'shield' as IconType, color: colors.risk.low },
    medium: { name: 'warning' as IconType, color: colors.risk.medium },
    high: { name: 'flag' as IconType, color: colors.risk.high },
    critical: { name: 'error' as IconType, color: colors.risk.critical },
  };

  const config = riskConfig[level];
  
  return <Icon name={config.name} color={config.color} {...props} />;
};

export default Icon;
