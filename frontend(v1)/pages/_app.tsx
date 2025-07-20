import type { AppProps } from 'next/app';
import '../src/index.css';
import { GameStateProvider } from '../src/state/GameStateContext';

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <GameStateProvider>
      <Component {...pageProps} />
    </GameStateProvider>
  );
}

export default MyApp;
