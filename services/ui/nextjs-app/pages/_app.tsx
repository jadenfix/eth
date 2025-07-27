import type { AppProps } from 'next/app';
import { ChakraProvider } from '@chakra-ui/react';
import ErrorBoundary from '../src/components/atoms/ErrorBoundary';
import Head from 'next/head';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <title>ETH Hackathon - Blockchain Intelligence Platform</title>
        <meta name="description" content="Palantir-grade blockchain intelligence and analytics platform" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      </Head>
      <ChakraProvider>
        <ErrorBoundary>
          <Component {...pageProps} />
        </ErrorBoundary>
      </ChakraProvider>
    </>
  );
}
