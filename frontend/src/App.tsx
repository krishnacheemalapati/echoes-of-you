import React, { useEffect } from 'react';
import { GameStateProvider, useGameState } from './state/GameStateContext';
import StartScreen from './screens/StartScreen';
import NarrativeScreen from './screens/NarrativeScreen';
import InterviewScreen from './screens/InterviewScreen';
import DailySummaryScreen from './screens/DailySummaryScreen';
import EndingScreen from './screens/EndingScreen';
import { getGameState } from './api/gameApi';

function MainRouter() {
  const { gameState, setGameState } = useGameState();

  useEffect(() => {
    // Resume session if sessionId in localStorage
    const sessionId = localStorage.getItem('sessionId');
    if (sessionId && !gameState) {
      getGameState(sessionId).then(data => {
        setGameState({ sessionId: data.sessionId, currentState: data.currentState, fullTranscriptHistory: data.fullTranscriptHistory });
      });
    }
    // eslint-disable-next-line
  }, []);

  if (!gameState) return <StartScreen />;
  if (gameState.currentState.endsWith('INTRO')) return <NarrativeScreen />;
  if (gameState.currentState.endsWith('INTERVIEW_PENDING')) return <InterviewScreen />;
  if (gameState.currentState.endsWith('SUMMARY')) return <DailySummaryScreen />;
  if (gameState.currentState.startsWith('ENDING')) return <EndingScreen />;
  return <div>Unknown state: {gameState.currentState}</div>;
}

export default function App() {
  return (
    <GameStateProvider>
      <MainRouter />
    </GameStateProvider>
  );
}
