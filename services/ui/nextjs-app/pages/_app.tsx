import type { AppProps } from 'next/app';
import { ThemeProvider } from '../src/providers/ThemeProvider';
import { LayoutProvider } from '../src/providers/LayoutProvider';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <LayoutProvider>
        <div role="note" style={{ background: '#fff8df', color: '#594400', padding: '10px 18px', fontSize: 12, textAlign: 'center' }}>
          Legacy sample preview · displayed metrics and activity are illustrative. Live chain and AI feeds are not connected.
        </div>
        <Component {...pageProps} />
      </LayoutProvider>
    </ThemeProvider>
  );
}
