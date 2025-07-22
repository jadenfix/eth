import React from 'react';
import { Spinner as ChakraSpinner, SpinnerProps as ChakraSpinnerProps, Box } from '@chakra-ui/react';
import { colors } from '../../theme/colors';
import { transitionPresets } from '../../theme/motion';

interface SpinnerProps extends Omit<ChakraSpinnerProps, 'size'> {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | number;
  variant?: 'default' | 'dots' | 'pulse' | 'bars' | 'ring';
  color?: string;
  label?: string;
}

const getSizeValue = (size: SpinnerProps['size']): string => {
  if (typeof size === 'number') return `${size}px`;
  
  const sizeMap = {
    xs: '12px',
    sm: '16px',
    md: '24px',
    lg: '32px',
    xl: '48px',
  };
  
  return sizeMap[size || 'md'];
};

// Default Chakra spinner
const DefaultSpinner: React.FC<SpinnerProps> = ({ size = 'md', color = colors.primary[600], label, ...props }) => (
  <ChakraSpinner
    thickness="2px"
    speed="0.65s"
    emptyColor="gray.200"
    color={color}
    size={size as any}
    label={label}
    {...props}
  />
);

// Custom dot spinner using CSS-in-JS
const DotSpinner: React.FC<SpinnerProps> = ({ size = 'md', color = colors.primary[600] }) => {
  const sizeValue = getSizeValue(size);
  
  return (
    <Box
      display="inline-flex"
      alignItems="center"
      justifyContent="center"
      width={sizeValue}
      height={sizeValue}
      sx={{
        '@keyframes dot-pulse': {
          '0%, 80%, 100%': {
            transform: 'scale(0)',
            opacity: 0.5,
          },
          '40%': {
            transform: 'scale(1)',
            opacity: 1,
          },
        },
      }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        width="100%"
      >
        <Box
          width="20%"
          height="20%"
          backgroundColor={color}
          borderRadius="50%"
          sx={{
            animation: 'dot-pulse 1.4s ease-in-out infinite both',
            animationDelay: '-0.32s',
          }}
        />
        <Box
          width="20%"
          height="20%"
          backgroundColor={color}
          borderRadius="50%"
          sx={{
            animation: 'dot-pulse 1.4s ease-in-out infinite both',
            animationDelay: '-0.16s',
          }}
        />
        <Box
          width="20%"
          height="20%"
          backgroundColor={color}
          borderRadius="50%"
          sx={{
            animation: 'dot-pulse 1.4s ease-in-out infinite both',
            animationDelay: '0s',
          }}
        />
      </Box>
    </Box>
  );
};

// Pulse spinner
const PulseSpinner: React.FC<SpinnerProps> = ({ size = 'md', color = colors.primary[600] }) => {
  const sizeValue = getSizeValue(size);
  
  return (
    <Box
      width={sizeValue}
      height={sizeValue}
      borderRadius="50%"
      bg={color}
      opacity={0.6}
      sx={{
        '@keyframes pulse': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
  );
};

// Bar spinner using CSS-in-JS
const BarSpinner: React.FC<SpinnerProps> = ({ size = 'md', color = colors.primary[600] }) => {
  const sizeValue = getSizeValue(size);
  
  return (
    <Box
      display="inline-flex"
      alignItems="center"
      justifyContent="center"
      width={sizeValue}
      height={sizeValue}
      sx={{
        '@keyframes bar-scale': {
          '0%, 40%, 100%': {
            transform: 'scaleY(0.4)',
          },
          '20%': {
            transform: 'scaleY(1)',
          },
        },
      }}
    >
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="flex-end"
        width="100%"
        height="100%"
      >
        <Box
          width="15%"
          height="100%"
          backgroundColor={color}
          borderRadius="1px"
          sx={{
            animation: 'bar-scale 1s ease-in-out infinite',
            animationDelay: '-0.4s',
          }}
        />
        <Box
          width="15%"
          height="100%"
          backgroundColor={color}
          borderRadius="1px"
          sx={{
            animation: 'bar-scale 1s ease-in-out infinite',
            animationDelay: '-0.3s',
          }}
        />
        <Box
          width="15%"
          height="100%"
          backgroundColor={color}
          borderRadius="1px"
          sx={{
            animation: 'bar-scale 1s ease-in-out infinite',
            animationDelay: '-0.2s',
          }}
        />
        <Box
          width="15%"
          height="100%"
          backgroundColor={color}
          borderRadius="1px"
          sx={{
            animation: 'bar-scale 1s ease-in-out infinite',
            animationDelay: '-0.1s',
          }}
        />
        <Box
          width="15%"
          height="100%"
          backgroundColor={color}
          borderRadius="1px"
          sx={{
            animation: 'bar-scale 1s ease-in-out infinite',
            animationDelay: '0s',
          }}
        />
      </Box>
    </Box>
  );
};

// Ring spinner
const RingSpinner: React.FC<SpinnerProps> = ({ size = 'md', color = colors.primary[600] }) => {
  const sizeValue = getSizeValue(size);
  
  return (
    <Box
      width={sizeValue}
      height={sizeValue}
      border="2px solid"
      borderColor="gray.200"
      borderTopColor={color}
      borderRadius="50%"
      sx={{
        '@keyframes spin': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        animation: 'spin 0.8s linear infinite',
      }}
    />
  );
};

export const Spinner: React.FC<SpinnerProps> = ({
  variant = 'default',
  ...props
}) => {
  switch (variant) {
    case 'dots':
      return <DotSpinner {...props} />;
    case 'pulse':
      return <PulseSpinner {...props} />;
    case 'bars':
      return <BarSpinner {...props} />;
    case 'ring':
      return <RingSpinner {...props} />;
    default:
      return <DefaultSpinner {...props} />;
  }
};

// Loading overlay component
interface LoadingOverlayProps {
  isLoading: boolean;
  children: React.ReactNode;
  spinner?: React.ReactNode;
  message?: string;
  backdrop?: boolean;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  children,
  spinner,
  message = 'Loading...',
  backdrop = true,
}) => {
  if (!isLoading) return <>{children}</>;

  return (
    <Box position="relative">
      {children}
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        bottom={0}
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        bg={backdrop ? 'blackAlpha.600' : 'transparent'}
        color="white"
        zIndex={10}
      >
        {spinner || <Spinner size="lg" color="white" />}
        {message && (
          <Box mt={4} fontSize="sm" fontWeight="medium">
            {message}
          </Box>
        )}
      </Box>
    </Box>
  );
};

// Full page loading component
interface PageLoadingProps {
  message?: string;
  spinner?: React.ReactNode;
}

export const PageLoading: React.FC<PageLoadingProps> = ({
  message = 'Loading application...',
  spinner,
}) => {
  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      bg="gray.50"
      zIndex={9999}
    >
      {spinner || <Spinner size="xl" variant="ring" />}
      {message && (
        <Box mt={6} fontSize="lg" fontWeight="medium" color="gray.600">
          {message}
        </Box>
      )}
    </Box>
  );
};

export default Spinner;
