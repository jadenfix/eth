import React from 'react';
import Head from 'next/head';
import { Box, Container, useColorModeValue } from '@chakra-ui/react';
import { ResponsiveNavBar } from '../molecules/ResponsiveNavBar';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
  maxWidth?: string;
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  children,
  title,
  description,
  maxWidth = '7xl'
}) => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  return (
    <>
      <Head>
        <title>{title}</title>
        {description && <meta name="description" content={description} />}
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#3182CE" />
      </Head>
      
      <Box bg={bgColor} minH="100vh">
        <ResponsiveNavBar />
        
        <Container 
          maxW={maxWidth} 
          px={{ base: 4, md: 6, lg: 8 }} 
          py={{ base: 4, md: 6, lg: 8 }}
        >
          {children}
        </Container>
      </Box>
    </>
  );
};
