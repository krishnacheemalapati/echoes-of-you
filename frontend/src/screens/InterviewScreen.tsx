import React, { useEffect, useState } from 'react';
import { checkInterviewStatus } from '../api/gameApi';
import { useGameState } from '../state/GameStateContext';

export default function InterviewScreen() {
  const { gameState, setGameState } = useGameState();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!gameState?.sessionId) return;
    let interval: NodeJS.Timeout;
    const poll = async () => {
      setLoading(true);
      const data = await checkInterviewStatus(gameState.sessionId);
      setLoading(false);
      if (data.currentState !== 'INTERVIEW_PENDING') {
        setGameState({ ...gameState, ...data });
      } else {
        interval = setTimeout(poll, 3000);
      }
    };
    poll();
    return () => clearTimeout(interval);
    // eslint-disable-next-line
  }, [gameState?.sessionId]);

  if (!gameState?.interviewLink) return <div>Loading interview...</div>;

  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className="text-xl font-semibold">Interview in Progress</h2>
      <iframe src={gameState.interviewLink} title="Ribbon Interview" width="600" height="400" className="border rounded" />
      {loading && <div>Checking interview status...</div>}
    </div>
  );
}
