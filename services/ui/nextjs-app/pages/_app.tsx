import type { AppProps } from 'next/app';
import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import { AnimatePresence } from 'framer-motion';
import ErrorBoundary from '../src/components/atoms/ErrorBoundary';
import Head from 'next/head';
import { enhancedTheme } from '../src/theme/enhanced';

export default function App({ Component, pageProps, router }: AppProps) {
  return (
    <>
      <Head>
        <title>Onchain Command Center - Blockchain Intelligence Platform</title>
        <meta name="description" content="Palantir-grade blockchain intelligence and analytics platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </Head>
      <ColorModeScript initialColorMode={enhancedTheme.config.initialColorMode} />
      <ChakraProvider theme={enhancedTheme}>
        <ErrorBoundary>
          <AnimatePresence mode="wait" initial={false}>
            <Component {...pageProps} key={router?.route || 'default'} />
          </AnimatePresence>
        </ErrorBoundary>
      </ChakraProvider>
    </>
  );
}
