import React from 'react';
import { useGameState } from '../state/GameStateContext';

export default function EndingScreen() {
  const { gameState, setGameState } = useGameState();

  const handleReturnToMenu = () => {
    setGameState(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('sessionId');
    }
  };

  const endingTitle = 'Game Over';
  let endingSubtitle = '';
  switch (gameState?.currentState) {
    case 'ENDING_CONTRADICTION':
      endingSubtitle = 'Contradiction Detected';
      break;
    case 'ENDING_GUILTY':
      endingSubtitle = 'Guilty';
      break;
    case 'ENDING_INNOCENT':
      endingSubtitle = 'Innocent';
      break;
    case 'ENDING_INCONCLUSIVE':
      endingSubtitle = 'Inconclusive';
      break;
    case 'ENDING_IMMUNE_EXECUTION':
      endingSubtitle = 'Immune to Truth Serum - Executed';
      break;
    default:
      endingSubtitle = gameState?.currentState?.replace('ENDING_', '') || '';
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className="text-2xl font-bold">{endingTitle}</h2>
      <div className="text-lg font-semibold">{endingSubtitle}</div>
      {gameState?.endingExplanation && (
        <div className="max-w-xl bg-gray-100 rounded p-4 mt-4">
          <pre className="text-xs bg-white rounded p-2 overflow-x-auto">{gameState.endingExplanation}</pre>
        </div>
      )}
      <button
        className="mt-8 px-6 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
        onClick={handleReturnToMenu}
      >
        Return to Main Menu
      </button>
    </div>
  );
}
