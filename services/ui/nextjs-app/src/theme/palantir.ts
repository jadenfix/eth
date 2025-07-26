import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
};

const theme = extendTheme({
  config,
  fonts: {
    heading: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    body: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    mono: 'SF Mono, Monaco, Inconsolata, "Roboto Mono", "Source Code Pro", monospace',
  },
  colors: {
    // Dark mode colors (Palantir-inspired)
    dark: {
      50: '#f7fafc',
      100: '#edf2f7',
      200: '#e2e8f0',
      300: '#cbd5e0',
      400: '#a0aec0',
      500: '#718096',
      600: '#4a5568',
      700: '#2d3748',
      800: '#1a202c',
      900: '#171923',
    },
    // Mystical crypto colors
    crypto: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
    },
    // Ethereum-inspired colors
    eth: {
      50: '#fef7ff',
      100: '#fdeeff',
      200: '#fbdfff',
      300: '#f7c0ff',
      400: '#f091ff',
      500: '#e855ff',
      600: '#d633ff',
      700: '#b300cc',
      800: '#8a0099',
      900: '#610066',
    },
    // Success/Error states
    success: {
      50: '#f0fdf4',
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#14532d',
    },
    error: {
      50: '#fef2f2',
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
    // Warning colors
    warning: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'medium',
        borderRadius: 'md',
        _focus: {
          boxShadow: 'outline',
        },
      },
      variants: {
        solid: {
          bg: 'crypto.600',
          color: 'white',
          _hover: {
            bg: 'crypto.700',
          },
          _active: {
            bg: 'crypto.800',
          },
        },
        ghost: {
          color: 'gray.300',
          _hover: {
            bg: 'whiteAlpha.100',
          },
        },
        outline: {
          borderColor: 'crypto.500',
          color: 'crypto.400',
          _hover: {
            bg: 'crypto.500',
            color: 'white',
          },
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          bg: 'dark.800',
          border: '1px solid',
          borderColor: 'dark.700',
          borderRadius: 'lg',
          boxShadow: 'lg',
        },
      },
    },
    Input: {
      baseStyle: {
        field: {
          bg: 'dark.700',
          border: '1px solid',
          borderColor: 'dark.600',
          _focus: {
            borderColor: 'crypto.500',
            boxShadow: '0 0 0 1px var(--chakra-colors-crypto-500)',
          },
        },
      },
    },
    Select: {
      baseStyle: {
        field: {
          bg: 'dark.700',
          border: '1px solid',
          borderColor: 'dark.600',
          _focus: {
            borderColor: 'crypto.500',
            boxShadow: '0 0 0 1px var(--chakra-colors-crypto-500)',
          },
        },
      },
    },
    Table: {
      baseStyle: {
        table: {
          bg: 'dark.800',
        },
        thead: {
          bg: 'dark.700',
        },
        th: {
          color: 'gray.300',
          fontWeight: 'semibold',
          borderBottom: '1px solid',
          borderColor: 'dark.600',
        },
        td: {
          borderBottom: '1px solid',
          borderColor: 'dark.700',
        },
      },
    },
    Badge: {
      baseStyle: {
        borderRadius: 'full',
        fontWeight: 'medium',
      },
      variants: {
        success: {
          bg: 'success.500',
          color: 'white',
        },
        error: {
          bg: 'error.500',
          color: 'white',
        },
        warning: {
          bg: 'warning.500',
          color: 'white',
        },
        info: {
          bg: 'crypto.500',
          color: 'white',
        },
      },
    },
  },
  styles: {
    global: (props: any) => ({
      body: {
        bg: props.colorMode === 'dark' ? 'dark.900' : 'gray.50',
        color: props.colorMode === 'dark' ? 'gray.100' : 'gray.900',
        fontFamily: 'body',
      },
      '*::placeholder': {
        color: props.colorMode === 'dark' ? 'gray.400' : 'gray.500',
      },
      'html, body': {
        height: '100%',
      },
      '#__next': {
        height: '100%',
      },
    }),
  },
});

export default theme; 