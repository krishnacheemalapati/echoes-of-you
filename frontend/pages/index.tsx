import React, { useContext } from 'react';
import StartScreen from '../src/screens/StartScreen';
import NarrativeScreen from '../src/screens/NarrativeScreen';
import InterviewScreen from '../src/screens/InterviewScreen';
import DailySummaryScreen from '../src/screens/DailySummaryScreen';
import EndingScreen from '../src/screens/EndingScreen';
import { GameStateContext } from '../src/state/GameStateContext';

const App: React.FC = () => {
  const { gameState } = useContext(GameStateContext);

  if (!gameState || !gameState.currentState) {
    return <StartScreen />;
  }

  // Show EndingScreen for any ENDING_* state
  if (gameState.currentState.startsWith('ENDING')) {
    return <EndingScreen />;
  }
  switch (gameState.currentState) {
    case 'START':
    case 'DAY_1_INTRO':
    case 'DAY_2_INTRO':
    case 'DAY_3_INTRO':
    case 'DAY_4_INTRO':
    case 'DAY_5_INTRO':
      return <NarrativeScreen />;
    case 'INTERVIEW_PENDING':
      return <InterviewScreen />;
    case 'DAY_1_SUMMARY':
    case 'DAY_2_SUMMARY':
    case 'DAY_3_SUMMARY':
    case 'DAY_4_SUMMARY':
    case 'DAY_5_SUMMARY':
      return <DailySummaryScreen />;
    default:
      return <StartScreen />;
  }
};

export default App;
