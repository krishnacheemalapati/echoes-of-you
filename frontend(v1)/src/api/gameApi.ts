

// Use environment variable or fallback for API base URL
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/game";

export async function getGameState(sessionId: string) {
  const res = await fetch(`${API_BASE}/${sessionId}`);
  if (!res.ok) throw new Error('Failed to fetch game state');
  return await res.json();
}

export async function startGame() {
  const res = await fetch(`${API_BASE}/start`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to start game');
  return await res.json();
}

export async function generateInterview(sessionId: string) {
  const res = await fetch(`${API_BASE}/${sessionId}/generate-interview`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to generate interview');
  // Expect { interviewLink, interviewId }
  return await res.json();
}

export async function checkInterviewStatus(sessionId: string) {
  const res = await fetch(`${API_BASE}/${sessionId}/check-interview-status`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to check interview status');
  return await res.json();
}

export async function nextDay(sessionId: string) {
  const res = await fetch(`${API_BASE}/${sessionId}/next-day`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to advance to next day');
  return await res.json();
}

export async function endGame(sessionId: string) {
  const res = await fetch(`${API_BASE}/${sessionId}/end`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to end game');
  return await res.json();
}
