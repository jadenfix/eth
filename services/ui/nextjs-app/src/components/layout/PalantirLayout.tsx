import React from 'react';
import { Box, useColorModeValue } from '@chakra-ui/react';
import PalantirNav from './PalantirNav';

interface PalantirLayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
}

const PalantirLayout: React.FC<PalantirLayoutProps> = ({ 
  children, 
  showSidebar = true 
}) => {
  const bg = useColorModeValue('gray.50', 'palantir.navy');

  return (
    <Box minH="100vh" bg={bg}>
      <PalantirNav />
      
      <Box
        pt="60px"
        pl={showSidebar ? "280px" : 0}
        transition="padding-left 0.3s ease"
      >
        <Box as="main" p={6}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default PalantirLayout; 