import React from 'react';
import { generateInterview } from '../api/gameApi';
import { useGameState } from '../state/GameStateContext';

export default function NarrativeScreen() {
  const { gameState, setGameState } = useGameState();

  const handleInterview = async () => {
    if (!gameState) return;
    const data = await generateInterview(gameState.sessionId);
    setGameState({ ...gameState, currentState: 'INTERVIEW_PENDING', interviewLink: data.interviewLink });
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className="text-xl font-semibold">Day {gameState?.day_number || 1} - Narrative</h2>
      <p className="max-w-xl text-center">The story unfolds... (insert narrative here)</p>
      <button className="px-6 py-2 bg-green-600 text-white rounded" onClick={handleInterview}>
        Begin Interview
      </button>
    </div>
  );
}
