import React, { useState, useEffect } from 'react';
import '../styles/App.css'; 
import cellBgVideo from '../assets/jailcell2050.mp4';
import interviewerImg from '../assets/interviewer.png';

const interviewerLines = [
  "Welcome. Let's begin.",
  "Tell me about yourself.",
  "Why do you think you're here?",
];

const PrisonCellLayout: React.FC = () => {
  const [currentLine, setCurrentLine] = useState(0);
  const [displayedText, setDisplayedText] = useState('');

  // Typewriter effect for text box
  useEffect(() => {
    setDisplayedText('');
    let i = 0;
    const interval = setInterval(() => {
      setDisplayedText(interviewerLines[currentLine].slice(0, i + 1));
      i++;
      if (i === interviewerLines[currentLine].length) clearInterval(interval);
    }, 40);
    return () => clearInterval(interval);
  }, [currentLine]);

  return (
    <div className="prison-cell-bg">
      <video
        autoPlay 
        loop    //
        muted
        playsInline 
        style={{
          position: 'absolute',
          width: '100vw',
          height: '100vh',
          objectFit: 'cover',
          left: 0,
          top: 0,
          zIndex: 0,
        }}
      >
        <source src={cellBgVideo} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      {/* <div className="cell-graphics" /> */}
      <div className="interviewer-area">
        <div className="avatar-container">
          <div 
            className="interviewer-avatar" 
            style={{ backgroundImage: `url(${interviewerImg})` }}
          />
          <div className="speech-bubble animate-bubble">
            {displayedText}
          </div>
        </div>
      </div>
      <div className="game-iframe-container">
        <iframe
          title="Game"
          src="about:blank"
          className="game-iframe"
        />
      </div>
      {/* Start Game Button */}
      <button className="start-game-btn">
        Start Interrogation
      </button>
    </div>
  );
};

export default PrisonCellLayout;