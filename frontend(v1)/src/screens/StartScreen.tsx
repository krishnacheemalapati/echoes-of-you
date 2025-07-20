import React from 'react';
import { startGame } from '../api/gameApi';
import { useGameState } from '../state/GameStateContext';

export default function StartScreen() {
  const { setGameState } = useGameState();

  const handleStart = async () => {
    const data = await startGame();
    setGameState({ sessionId: data.sessionId, currentState: 'DAY_1_INTRO', fullTranscriptHistory: [] });
    localStorage.setItem('sessionId', data.sessionId);
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <h1 className="text-3xl font-bold">Echoes of You</h1>
      <button className="px-6 py-2 bg-blue-600 text-white rounded" onClick={handleStart}>
        Start New Game
      </button>
    </div>
  );
}
