/**
 * Enhanced Theme Management System
 * Combining Palantir Blueprint + ChatGPT + Apple HIG design languages
 */

import { extendTheme, type ThemeConfig } from '@chakra-ui/react';

// Theme configuration
const config: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
};

// Color palette combining all three design systems
const colors = {
  // Palantir Blueprint
  palantir: {
    50: '#E6F4FF',
    100: '#BAE0FF', 
    200: '#91CAFF',
    300: '#69B1FF',
    400: '#4096FF',
    500: '#14C8FF', // Primary teal
    600: '#1677FF',
    700: '#0958D9',
    800: '#003EB3',
    900: '#002C8C',
    navy: '#0F1B2D', // Primary navy background
    'navy-light': '#1A2332',
    'navy-dark': '#0A1018',
  },
  // ChatGPT inspired
  chatgpt: {
    stone: '#F7F7F8',
    graphite: '#2D2E33', 
    success: '#10A37F',
    border: '#E5E5E5',
    'text-light': '#374151',
    'text-dark': '#F9FAFB',
  },
  // Apple HIG semantic colors
  apple: {
    blue: '#007AFF',
    green: '#34C759',
    orange: '#FF9500', 
    red: '#FF3B30',
    purple: '#AF52DE',
    pink: '#FF2D92',
    yellow: '#FFCC00',
    gray: '#8E8E93',
  },
  // Enhanced brand colors
  brand: {
    50: '#E6F7FF',
    100: '#BAE7FF',
    200: '#91D5FF', 
    300: '#69C0FF',
    400: '#40A9FF',
    500: '#14C8FF', // Main brand color
    600: '#1890FF',
    700: '#096DD9',
    800: '#0050B3',
    900: '#003A8C',
  },
};

// Typography scale following Apple HIG
const fonts = {
  heading: `'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif`,
  body: `'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, sans-serif`,
  mono: `'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace`,
};

const fontSizes = {
  xs: '12px',
  sm: '14px', 
  md: '16px',
  lg: '18px',
  xl: '20px',
  '2xl': '24px',
  '3xl': '30px',
  '4xl': '36px',
  '5xl': '48px',
  '6xl': '60px',
  '7xl': '72px',
  '8xl': '96px',
  '9xl': '128px',
};

// Component style overrides
const components = {
  Button: {
    baseStyle: {
      fontWeight: '600',
      borderRadius: 'lg',
      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      _hover: {
        transform: 'translateY(-1px)',
        boxShadow: 'lg',
      },
      _active: {
        transform: 'translateY(0)',
      },
    },
    variants: {
      solid: {
        bg: 'brand.500',
        color: 'white',
        _hover: {
          bg: 'brand.600',
          boxShadow: '0 0 20px rgba(20, 200, 255, 0.4)',
        },
      },
      ghost: {
        _hover: {
          bg: 'palantir.navy-light',
        },
      },
      magnetic: {
        position: 'relative',
        overflow: 'hidden',
        _before: {
          content: '""',
          position: 'absolute',
          top: 0,
          left: '-100%',
          width: '100%',
          height: '100%',
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
          transition: 'left 0.5s',
        },
        _hover: {
          _before: {
            left: '100%',
          },
        },
      },
    },
  },
  Card: {
    baseStyle: {
      container: {
        borderRadius: 'xl',
        border: '1px solid',
        borderColor: 'gray.200',
        _dark: {
          borderColor: 'gray.600',
          bg: 'palantir.navy-light',
        },
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        _hover: {
          transform: 'scale(1.02)',
          boxShadow: 'xl',
          _dark: {
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.4)',
          },
        },
      },
    },
  },
  Badge: {
    baseStyle: {
      borderRadius: 'full',
      fontWeight: '600',
      fontSize: 'xs',
      px: 3,
      py: 1,
    },
    variants: {
      glow: {
        bg: 'brand.500',
        color: 'white',
        boxShadow: '0 0 10px rgba(20, 200, 255, 0.6)',
        animation: 'glow 2s ease-in-out infinite alternate',
      },
    },
  },
  Stat: {
    baseStyle: {
      container: {
        bg: 'transparent',
        _hover: {
          bg: 'gray.50',
          _dark: {
            bg: 'palantir.navy-light',
          },
        },
        borderRadius: 'lg',
        p: 4,
        transition: 'all 0.2s',
      },
      number: {
        fontSize: '2xl',
        fontWeight: 'bold',
        color: 'brand.500',
      },
      label: {
        color: 'gray.600',
        _dark: {
          color: 'gray.300',
        },
        fontSize: 'sm',
        fontWeight: '500',
      },
    },
  },
};

// Global styles
const styles = {
  global: (props: any) => ({
    'html, body': {
      fontFamily: 'body',
      color: props.colorMode === 'dark' ? 'chatgpt.text-dark' : 'chatgpt.text-light',
      bg: props.colorMode === 'dark' ? 'palantir.navy' : 'white',
      lineHeight: 'tall',
      scrollBehavior: 'smooth',
    },
    '*::placeholder': {
      color: props.colorMode === 'dark' ? 'gray.400' : 'gray.500',
    },
    '*, *::before, &::after': {
      borderColor: props.colorMode === 'dark' ? 'gray.600' : 'gray.200',
      wordWrap: 'break-word',
    },
    // Smooth scrollbar
    '::-webkit-scrollbar': {
      width: '8px',
    },
    '::-webkit-scrollbar-track': {
      bg: props.colorMode === 'dark' ? 'gray.800' : 'gray.100',
    },
    '::-webkit-scrollbar-thumb': {
      bg: props.colorMode === 'dark' ? 'gray.600' : 'gray.400',
      borderRadius: 'full',
      _hover: {
        bg: props.colorMode === 'dark' ? 'gray.500' : 'gray.500',
      },
    },
    // Enhanced focus styles
    '*:focus': {
      outline: 'none',
      boxShadow: `0 0 0 3px rgba(20, 200, 255, 0.5)`,
    },
  }),
};

// Create the enhanced theme
export const enhancedTheme = extendTheme({
  config,
  colors,
  fonts,
  fontSizes,
  components,
  styles,
  semanticTokens: {
    colors: {
      'bg-primary': {
        default: 'white',
        _dark: 'palantir.navy',
      },
      'bg-secondary': {
        default: 'gray.50',
        _dark: 'palantir.navy-light',
      },
      'text-primary': {
        default: 'gray.900',
        _dark: 'white',
      },
      'text-secondary': {
        default: 'gray.600', 
        _dark: 'gray.300',
      },
      'border-primary': {
        default: 'gray.200',
        _dark: 'gray.600',
      },
    },
  },
});

// Theme toggle utilities
export const useTheme = () => {
  if (typeof window !== 'undefined') {
    const getTheme = () => localStorage.getItem('chakra-ui-color-mode') || 'dark';
    const setTheme = (theme: 'light' | 'dark') => {
      localStorage.setItem('chakra-ui-color-mode', theme);
      document.documentElement.setAttribute('data-theme', theme);
      document.documentElement.classList.toggle('dark', theme === 'dark');
    };
    
    return { getTheme, setTheme };
  }
  return { getTheme: () => 'dark', setTheme: () => {} };
};

export default enhancedTheme;
