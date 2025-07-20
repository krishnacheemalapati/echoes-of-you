import React, { createContext, useContext, useState, ReactNode } from 'react';

export type GameState = {
  sessionId: string;
  currentState: string;
  fullTranscriptHistory: any[];
  day_number?: number;
  interviewLink?: string;
  interviewId?: string;
  endingExplanation?: string;
};

interface GameStateContextType {
  gameState: GameState | null;
  setGameState: (state: GameState | null) => void;
}

export const GameStateContext = createContext<GameStateContextType | undefined>(undefined);

export function GameStateProvider({ children }: { children: ReactNode }) {
  const [gameState, setGameState] = useState<GameState | null>(null);
  return (
    <GameStateContext.Provider value={{ gameState, setGameState }}>
      {children}
    </GameStateContext.Provider>
  );
}

export function useGameState() {
  const ctx = useContext(GameStateContext);
  if (!ctx) throw new Error('useGameState must be used within GameStateProvider');
  return ctx;
}
