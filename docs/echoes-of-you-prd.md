# Echoes of You: Visual Novel Game - Product Requirements Document (PRD)

## Overview

Echoes of You is a visual novel set in a dystopian world where a potent truth serum has revolutionized the justice system. Players wake up in a prison, accused of a crime they do not remember. Through a series of interactive interviews powered by AI (ChatGPT), players uncover memories, answer questions, and influence the narrative, ultimately leading to one of several possible endings based on their responses.

## Goals
- Deliver a replayable, narrative-driven game with high player agency.
- Integrate AI-driven interviews that adapt to player choices.
- Provide a seamless, immersive UI/UX for both story and interview segments.

## Key Features
- **Dynamic Interview System:** Embedded Ribbon interviews in iframes, with questions generated and adapted by ChatGPT.
- **Branching Narrative:** Player responses influence subsequent interviews and the final outcome.
- **Memory/Area Progression:** Game is divided into key memories/areas, each unlocking new interview segments.
- **Multiple Endings:** Endings are determined by AI analysis of player responses.
- **Replayability:** Each playthrough can reveal new information or outcomes.
- **Front-End, Back-End, and Database Integration:** Persistent player data, interview history, and branching logic.

## User Stories

### 1. As a player, I want to experience a compelling narrative where my choices matter, so that I feel immersed and invested in the outcome.
- **Acceptance Criteria:**
  - The game presents a clear story premise and stakes.
  - Player choices during interviews affect the narrative and ending.

### 2. As a player, I want to participate in AI-driven interviews that adapt to my answers, so that each playthrough feels unique.
- **Acceptance Criteria:**
  - Each interview is embedded via an iframe and powered by ChatGPT.
  - Questions in later interviews reference previous answers.

### 3. As a player, I want to progress through different memories/areas, so that I can piece together the mystery of the crime.
- **Acceptance Criteria:**
  - The game is divided into distinct areas/memories with vague names.
  - Each area unlocks a new interview segment.

### 4. As a player, I want the game to track my responses and progress, so that my experience is persistent and meaningful.
- **Acceptance Criteria:**
  - Player responses and interview history are stored in a database.
  - The game can resume from the last completed area/interview.

### 5. As a player, I want to see a clear ending based on my choices, so that my actions feel impactful.
- **Acceptance Criteria:**
  - The game presents one of several endings based on AI analysis of player responses.
  - Endings are distinct and reflect the player's journey.

## Open Questions
**Should the crime be the same on every playthrough, or randomized?**
  - The crime should be the same for now, unless the user indicates otherwise.

**What level of information should be revealed in each playthrough to maximize replayability?**
  - Minimal. Just enough that the player can start to put the pieces together over the course of several interviews.

**What is the desired visual style/theme for the UI?**
  - Recommendation: A minimalist, moody, and atmospheric style. Use a muted color palette (grays, blues, and deep purples) with high-contrast highlights for interactive elements. Incorporate subtle animations and visual effects (e.g., flickering lights, blurred backgrounds) to evoke a sense of unease and dystopian tension. Typography should be clean and modern, with clear separation between narrative and interview segments.

**Should players be able to save and load progress manually, or is auto-save sufficient?**
  - Auto-save is sufficient.

**How are player choices tracked and visualized?**
  - Player choices are not visually tracked; players must keep track of their own answers, simulating a real interview experience.

**What accessibility features will be included?**
  - None planned for the hackathon version.

**How will the AI (ChatGPT) be prompted and managed?**
  - To be decided by the development team for speed and simplicity; focus on quick, effective prompt engineering.

**Will analytics or telemetry be collected?**
  - No telemetry or analytics will be collected; this is a hackathon project.

**Will there be support for localization or multiple languages?**
  - No; the game will support only one language.

**What is the target platform?**
  - Web only.

**How will updates be managed after launch?**
  - No updates are planned after launch; post-launch support is not required.
- Specify the data model for storing player progress and responses.
- Develop prompt engineering guidelines for ChatGPT interview generation.

---

*Last updated: July 19, 2025*
