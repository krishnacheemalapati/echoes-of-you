import React from 'react';
import { useGameState } from '../state/GameStateContext';

export default function EndingScreen() {
  const { gameState } = useGameState();
  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className="text-2xl font-bold">Ending</h2>
      <div className="text-lg font-semibold">{gameState?.currentState?.replace('ENDING_', '')}</div>
      {gameState?.endingExplanation && (
        <div className="max-w-xl bg-gray-100 rounded p-4 mt-4">
          <pre className="text-xs bg-white rounded p-2 overflow-x-auto">{gameState.endingExplanation}</pre>
        </div>
      )}
      <div className="mt-8">Thank you for playing Echoes of You.</div>
    </div>
  );
}
