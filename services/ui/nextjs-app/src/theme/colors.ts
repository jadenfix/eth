// Design tokens for consistent theming across the application
export const colors = {
  // Primary brand colors
  primary: {
    50: '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
  },
  
  // Semantic colors for risk levels
  risk: {
    low: '#10b981',
    medium: '#f59e0b',
    high: '#ef4444',
    critical: '#dc2626',
  },
  
  // Entity type colors
  entity: {
    address: '#3b82f6',
    contract: '#10b981',
    token: '#f59e0b',
    transaction: '#ef4444',
    block: '#8b5cf6',
  },
  
  // Grayscale for backgrounds and text
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
  
  // Status colors
  success: '#10b981',
  warning: '#f59e0b',
  error: '#ef4444',
  info: '#3b82f6',
  
  // Background colors
  background: {
    primary: '#ffffff',
    secondary: '#f9fafb',
    dark: '#1f2937',
    panel: '#ffffff',
    overlay: 'rgba(0, 0, 0, 0.5)',
  },
  
  // Border colors
  border: {
    light: '#e5e7eb',
    medium: '#d1d5db',
    dark: '#4b5563',
  },
  
  // Text colors
  text: {
    primary: '#111827',
    secondary: '#6b7280',
    tertiary: '#9ca3af',
    inverse: '#ffffff',
  },
} as const;

// Color utilities
export const getEntityColor = (entityType: string): string => {
  return colors.entity[entityType as keyof typeof colors.entity] || colors.gray[500];
};

export const getRiskColor = (riskLevel: string): string => {
  return colors.risk[riskLevel as keyof typeof colors.risk] || colors.gray[500];
};

export const getStatusColor = (status: 'success' | 'warning' | 'error' | 'info'): string => {
  return colors[status];
};

// Chakra UI theme integration
export const chakraColors = {
  ...colors,
  brand: colors.primary,
};
