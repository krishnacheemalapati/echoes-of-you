
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
      console.log('[InterviewScreen] Polling checkInterviewStatus for sessionId:', gameState.sessionId);
      const data = await checkInterviewStatus(gameState.sessionId);
      setLoading(false);
      console.log('[InterviewScreen] checkInterviewStatus response:', data);
      // Only end interview if currentState is NOT INTERVIEW_PENDING or DAY_X_INTERVIEW_PENDING
      const isInterviewPending =
        data.currentState === 'INTERVIEW_PENDING' ||
        /^DAY_\d+_INTERVIEW_PENDING$/.test(data.currentState || '');
      if (!isInterviewPending) {
        // Interview is over, clear interviewLink and interviewId
        console.log('[InterviewScreen] Interview ended, updating gameState:', { ...gameState, ...data, interviewLink: undefined, interviewId: undefined });
        setGameState({ ...gameState, ...data, interviewLink: undefined, interviewId: undefined });
      } else {
        interval = setTimeout(poll, 3000);
      }
    };
    poll();
    return () => clearTimeout(interval);
    // eslint-disable-next-line
  }, [gameState?.sessionId]);

  useEffect(() => {
    console.log('[InterviewScreen] Rendered with gameState:', gameState);
  }, [gameState]);

  if (!gameState?.interviewLink) {
    console.log('[InterviewScreen] No interviewLink, loading...');
    return <div>Loading interview...</div>;
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <h2 className="text-xl font-semibold">Interview in Progress</h2>
      <iframe
        src={gameState.interviewLink}
        title="Ribbon Interview"
        width="600"
        height="400"
        className="border rounded"
        allow="camera; microphone; clipboard-write; display-capture; autoplay"
        allowFullScreen
      />
      {loading && <div>Checking interview status...</div>}
    </div>
  );
}
