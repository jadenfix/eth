import React from 'react';
import { Box, Flex, useBreakpointValue, Heading, Text } from '@chakra-ui/react';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  title?: string;
  description?: string;
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  sidebar,
  header,
  footer,
  title,
  description
}) => {
  const isMobile = useBreakpointValue({ base: true, md: false });

  return (
    <Flex direction="column" h="100vh">
      {header && (
        <Box as="header" bg="white" borderBottom="1px solid" borderColor="gray.200" p={4}>
          {header}
        </Box>
      )}
      
      {title && (
        <Box as="header" bg="white" borderBottom="1px solid" borderColor="gray.200" p={4}>
          <Heading size="lg" mb={2}>{title}</Heading>
          {description && <Text color="gray.600">{description}</Text>}
        </Box>
      )}
      
      <Flex flex="1" overflow="hidden">
        {sidebar && !isMobile && (
          <Box as="aside" w="280px" bg="gray.50" borderRight="1px solid" borderColor="gray.200">
            {sidebar}
          </Box>
        )}
        
        <Box as="main" flex="1" overflow="auto" p={4}>
          {children}
        </Box>
      </Flex>
      
      {footer && (
        <Box as="footer" bg="white" borderTop="1px solid" borderColor="gray.200" p={4}>
          {footer}
        </Box>
      )}
    </Flex>
  );
}; 