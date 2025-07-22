import React from 'react';
import { ChakraProvider, extendTheme, type ThemeConfig } from '@chakra-ui/react';
import { colors } from '../theme/colors';
import { fonts, fontSizes, fontWeights } from '../theme/typography';
import { transitionPresets } from '../theme/motion';

// Extend Chakra UI theme with our custom design tokens
const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: true,
};

const theme = extendTheme({
  config,
  colors: {
    primary: colors.primary,
    gray: colors.gray,
    semantic: {
      success: colors.success,
      warning: colors.warning,
      error: colors.error,
      info: colors.info,
    },
    risk: colors.risk,
    entity: colors.entity,
  },
  fonts: {
    heading: fonts.heading,
    body: fonts.body,
    mono: fonts.mono,
  },
  fontSizes,
  fontWeights,
  transitions: {
    property: {
      common: 'background-color, border-color, color, fill, stroke, opacity, box-shadow, transform',
    },
    easing: {
      ease: 'cubic-bezier(0.25, 0.1, 0.25, 1.0)',
      'ease-in': 'cubic-bezier(0.42, 0, 1, 1)',
      'ease-out': 'cubic-bezier(0, 0, 0.58, 1)',
      'ease-in-out': 'cubic-bezier(0.42, 0, 0.58, 1)',
    },
    duration: {
      'ultra-fast': '50ms',
      faster: '100ms',
      fast: '150ms',
      normal: '200ms',
      slow: '300ms',
      slower: '400ms',
      'ultra-slow': '500ms',
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'medium',
        borderRadius: 'md',
        transition: transitionPresets.button,
      },
      variants: {
        primary: {
          bg: 'primary.600',
          color: 'white',
          _hover: {
            bg: 'primary.700',
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: 'primary.800',
            transform: 'translateY(0px)',
          },
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          borderRadius: 'lg',
          boxShadow: 'md',
          transition: transitionPresets.hover,
          _hover: {
            boxShadow: 'lg',
          },
        },
      },
    },
    Modal: {
      baseStyle: {
        dialog: {
          borderRadius: 'xl',
          boxShadow: '2xl',
        },
        overlay: {
          backdropFilter: 'blur(4px)',
        },
      },
    },
  },
  styles: {
    global: (props: any) => ({
      body: {
        bg: props.colorMode === 'dark' ? 'gray.900' : 'gray.50',
        color: props.colorMode === 'dark' ? 'white' : 'gray.800',
        fontFamily: 'body',
      },
      '*::placeholder': {
        color: props.colorMode === 'dark' ? 'gray.400' : 'gray.500',
      },
      '*, *::before, &::after': {
        borderColor: props.colorMode === 'dark' ? 'gray.600' : 'gray.200',
      },
    }),
  },
});

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  return (
    <ChakraProvider theme={theme} resetCSS>
      {children}
    </ChakraProvider>
  );
};

export default ThemeProvider;
