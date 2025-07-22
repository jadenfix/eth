import React from 'react';
import { Button as ChakraButton, ButtonProps as ChakraButtonProps } from '@chakra-ui/react';
import { colors, getStatusColor } from '../../theme/colors';
import { textStyles } from '../../theme/typography';
import { transitionPresets } from '../../theme/motion';

interface ButtonProps extends Omit<ChakraButtonProps, 'variant'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline' | 'danger' | 'success';
  isLoading?: boolean;
  leftIcon?: React.ReactElement;
  rightIcon?: React.ReactElement;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  disabled,
  ...props
}) => {
  const getVariantStyles = (variant: string) => {
    switch (variant) {
      case 'primary':
        return {
          bg: colors.primary[600],
          color: 'white',
          _hover: {
            bg: colors.primary[700],
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: colors.primary[800],
            transform: 'translateY(0px)',
          },
          _disabled: {
            bg: colors.gray[300],
            color: colors.gray[500],
            cursor: 'not-allowed',
            _hover: { transform: 'none' },
          },
        };
      
      case 'secondary':
        return {
          bg: colors.gray[100],
          color: colors.gray[700],
          _hover: {
            bg: colors.gray[200],
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: colors.gray[300],
            transform: 'translateY(0px)',
          },
        };
      
      case 'ghost':
        return {
          bg: 'transparent',
          color: colors.primary[600],
          _hover: {
            bg: colors.primary[50],
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: colors.primary[100],
            transform: 'translateY(0px)',
          },
        };
      
      case 'outline':
        return {
          bg: 'transparent',
          color: colors.primary[600],
          border: `1px solid ${colors.primary[600]}`,
          _hover: {
            bg: colors.primary[50],
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: colors.primary[100],
            transform: 'translateY(0px)',
          },
        };
      
      case 'danger':
        return {
          bg: colors.error,
          color: 'white',
          _hover: {
            bg: '#dc2626',
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: '#b91c1c',
            transform: 'translateY(0px)',
          },
        };
      
      case 'success':
        return {
          bg: colors.success,
          color: 'white',
          _hover: {
            bg: '#059669',
            transform: 'translateY(-1px)',
          },
          _active: {
            bg: '#047857',
            transform: 'translateY(0px)',
          },
        };
      
      default:
        return {};
    }
  };

  return (
    <ChakraButton
      size={size}
      isLoading={isLoading}
      disabled={disabled || isLoading}
      leftIcon={leftIcon}
      rightIcon={rightIcon}
      transition={transitionPresets.button}
      fontWeight={textStyles.button.fontWeight}
      letterSpacing={textStyles.button.letterSpacing}
      borderRadius="md"
      {...getVariantStyles(variant)}
      {...props}
    >
      {children}
    </ChakraButton>
  );
};

// Button group for related actions
interface ButtonGroupProps {
  children: React.ReactNode;
  spacing?: number;
  orientation?: 'horizontal' | 'vertical';
  isAttached?: boolean;
}

export const ButtonGroup: React.FC<ButtonGroupProps> = ({
  children,
  spacing = 2,
  orientation = 'horizontal',
  isAttached = false,
}) => {
  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: orientation === 'vertical' ? 'column' : 'row',
    gap: isAttached ? 0 : spacing,
  };

  if (isAttached) {
    return (
      <div style={containerStyles} role="group">
        {React.Children.map(children, (child, index) => {
          if (React.isValidElement(child)) {
            const isFirst = index === 0;
            const isLast = index === React.Children.count(children) - 1;
            
            return React.cloneElement(child as any, {
              borderRadius: isFirst ? (orientation === 'horizontal' ? 'md 0 0 md' : 'md md 0 0') : 
                           isLast ? (orientation === 'horizontal' ? '0 md md 0' : '0 0 md md') : '0',
            });
          }
          return child;
        })}
      </div>
    );
  }

  return <div style={containerStyles}>{children}</div>;
};

export default Button;
