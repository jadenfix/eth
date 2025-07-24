/**
 * Enhanced App Layout
 * Combining Palantir + ChatGPT + Apple HIG design systems
 */

import React, { useState, useEffect } from 'react';
import { Box, useColorMode } from '@chakra-ui/react';
import { motion, AnimatePresence } from 'framer-motion';
import TopNav from './TopNav';
import SideRail from './SideRail';
import ActivityDrawer from './ActivityDrawer';

const MotionBox = motion(Box);

interface EnhancedLayoutProps {
  children: React.ReactNode;
}

const EnhancedLayout: React.FC<EnhancedLayoutProps> = ({ children }) => {
  const { colorMode } = useColorMode();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isActivityDrawerOpen, setIsActivityDrawerOpen] = useState(false);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Cmd/Ctrl + K for search
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        // TODO: Open command palette
      }
      
      // Cmd/Ctrl + \ for sidebar toggle
      if ((event.metaKey || event.ctrlKey) && event.key === '\\') {
        event.preventDefault();
        setIsSidebarOpen(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Auto-close sidebar on mobile
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 1024) {
        setIsSidebarOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Check initial size

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <Box
      minH="100vh"
      bg={colorMode === 'dark' ? 'palantir.navy' : 'white'}
      color={colorMode === 'dark' ? 'white' : 'gray.900'}
      display="grid"
      gridTemplateAreas={{
        base: `"nav nav"
               "content content"`,
        lg: `"nav nav nav"
             "sidebar content aside"`,
      }}
      gridTemplateColumns={{
        base: '1fr',
        lg: `${isSidebarOpen ? '280px' : '72px'} 1fr ${isActivityDrawerOpen ? '320px' : '0px'}`,
      }}
      gridTemplateRows="48px 1fr"
      transition="grid-template-columns 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
    >
      {/* Top Navigation */}
      <Box gridArea="nav">
        <TopNav
          onSidebarToggle={() => setIsSidebarOpen(prev => !prev)}
          isSidebarOpen={isSidebarOpen}
        />
      </Box>

      {/* Side Navigation */}
      <Box gridArea="sidebar" display={{ base: 'none', lg: 'block' }}>
        <SideRail
          isOpen={isSidebarOpen}
          onToggle={() => setIsSidebarOpen(prev => !prev)}
        />
      </Box>

      {/* Main Content */}
      <MotionBox
        gridArea="content"
        overflow="auto"
        position="relative"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <AnimatePresence mode="wait">
          <MotionBox
            key={typeof window !== 'undefined' ? window.location.pathname : 'content'}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            p={{ base: 4, md: 6, lg: 8 }}
            maxW="100%"
          >
            {children}
          </MotionBox>
        </AnimatePresence>
      </MotionBox>

      {/* Activity Drawer */}
      <Box gridArea="aside" display={{ base: 'none', lg: 'block' }}>
        <ActivityDrawer
          isOpen={isActivityDrawerOpen}
          onClose={() => setIsActivityDrawerOpen(false)}
        />
      </Box>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <MotionBox
            position="fixed"
            top="48px"
            left={0}
            w="100vw"
            h="calc(100vh - 48px)"
            bg="blackAlpha.600"
            zIndex={998}
            display={{ base: 'block', lg: 'none' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsSidebarOpen(false)}
          >
            <MotionBox
              w="280px"
              h="100%"
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              onClick={(e) => e.stopPropagation()}
            >
              <SideRail
                isOpen={true}
                onToggle={() => setIsSidebarOpen(false)}
              />
            </MotionBox>
          </MotionBox>
        )}
      </AnimatePresence>

      {/* Floating Action Button for Activity Drawer */}
      <MotionBox
        position="fixed"
        bottom={6}
        right={6}
        zIndex={1000}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        <Box
          w={12}
          h={12}
          borderRadius="full"
          bg="brand.500"
          color="white"
          display="flex"
          alignItems="center"
          justifyContent="center"
          cursor="pointer"
          boxShadow="xl"
          _hover={{
            bg: 'brand.600',
            boxShadow: '0 0 30px rgba(20, 200, 255, 0.5)',
          }}
          transition="all 0.2s"
          onClick={() => setIsActivityDrawerOpen(prev => !prev)}
        >
          <Box fontSize="lg">🔔</Box>
        </Box>
      </MotionBox>
    </Box>
  );
};

export default EnhancedLayout;
