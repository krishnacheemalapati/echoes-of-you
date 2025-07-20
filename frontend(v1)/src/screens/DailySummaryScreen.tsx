import React from 'react';
import { nextDay } from '../api/gameApi';
import { useGameState } from '../state/GameStateContext';

export default function DailySummaryScreen() {
  const { gameState, setGameState } = useGameState();
  const lastTwo = gameState?.fullTranscriptHistory?.slice(-2) || [];

  const handleContinue = async () => {
    if (!gameState) return;
    const data = await nextDay(gameState.sessionId);
    setGameState({ ...gameState, ...data });
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className="text-xl font-semibold">Daily Summary</h2>
      <div className="w-full max-w-xl bg-gray-100 rounded p-4">
        {lastTwo.length === 0 && <div>No transcripts yet.</div>}
        {lastTwo.map((t, i) => (
          <pre key={i} className="text-xs bg-white rounded p-2 my-2 overflow-x-auto">{JSON.stringify(t, null, 2)}</pre>
        ))}
      </div>
      <button className="px-6 py-2 bg-blue-600 text-white rounded" onClick={handleContinue}>
        Continue
      </button>
    </div>
  );
}
