You are a software engineer tasked with implementing the feature described in the attached file. If anything is unclear, ask me questions before starting. You must complete all steps in the document. After finishing, verify that all steps are complete; if not, return and implement the missing steps. Repeat this process until all steps are done.

# Echoes of You: Visual Novel Game - Technical Specification (Python/React/Ribbon)

## 1. Overview


This document outlines the technical design for "Echoes of You," a web-based visual novel. The architecture uses a Python (Django) backend with Django REST Framework, a React frontend, and the **Ribbon API** for conducting AI-powered voice interviews.

**Assumptions:**
- A Python 3.8+ environment is available for the backend.
- The frontend is a modern single-page application (SPA) built with React.
- API keys for an LLM service (e.g., OpenAI, Gemini via LangChain) and the **Ribbon API** will be managed as environment variables.
- The Ribbon API will be used to conduct the interviews. Our application will dynamically generate the questions for each interview, provide the user with a link to the Ribbon interview (embedded in an iframe), and retrieve the transcript upon completion.

## 2. Architecture

The application will consist of three main components:

1.  **Front-End:** A client-side application built with React (using Next.js). It will handle the UI, display the narrative, and embed the Ribbon interview within an iframe.
2.  **Back-End:** A robust Python server using the Django framework and Django REST Framework. It will manage the overall game state, use LangChain to generate questions and analyze final transcripts, and interact with both the Ribbon API and our database.
3.  **Database:** A PostgreSQL database, managed with Django ORM, to persist game sessions and transcripts.

## 3. Implementation Steps

### Step 1: Project Setup

1.  Create a root directory for the project.
2.  Inside the root, create two subdirectories: `frontend` and `backend`.
3.  **Backend:**
    -   Set up a Python virtual environment.
    -   Install dependencies: `django`, `djangorestframework`, `psycopg2-binary`, `langchain`, `langchain-openai` (or other provider), and `httpx` (for making API calls to Ribbon).
    -   Create a `.env` file or use Django settings for `LLM_API_KEY`, `RIBBON_API_KEY`, and database credentials.
    -   Initialize a new Django project and app (e.g., `gamesession`).
4.  **Frontend:**
    -   Initialize a new React project using Next.js (`npx create-next-app@latest`).
    -   Install `axios` for making API calls to our backend.

### Step 2: Database Schema (Django ORM)

1.  In the `backend` directory, configure Django to use a PostgreSQL database. Use environment variables or Django settings for the connection string.
2.  Define a `GameSession` model in Django with the following fields:
    *   `session_id` (CharField, primary_key=True): A unique identifier for each playthrough.
    *   `current_state` (CharField): The player's current stage (e.g., "DAY_1_INTRO", "DAY_1_INTERVIEW_PENDING", "DAY_1_SUMMARY").
    *   `day_number` (IntegerField): The current day/round of interviews the player is on.
    *   `full_transcript_history` (JSONField): A list storing the full transcript objects from all completed Ribbon interviews.
    *   `created_at` (DateTimeField): Timestamp of when the session started.
3.  Use Django's built-in migration system:
    -   `python manage.py makemigrations`
    -   `python manage.py migrate`


### Step 3: Back-End API Design (Django REST Framework)

-   **`POST /api/game/start`**
    -   **Purpose:** Initializes a new game session.
    -   **Action:** Generates a unique `session_id`, creates a new `GameSession` record.
    -   **Response:** `{ "sessionId": "..." }`

-   **`GET /api/game/{session_id}`**
    -   **Purpose:** Fetches the current state of a game session.
    -   **Response:** `{ "sessionId": "...", "currentState": "...", "fullTranscriptHistory": [...] }`

-   **`POST /api/game/{session_id}/generate-interview`**
    -   **Purpose:** Generates questions and creates a new Ribbon interview link.
    -   **Action:**
        1.  Use LangChain to generate interview questions based on the `full_transcript_history`. For the first interview, use the initial prompt.
        2.  Call Ribbon's `POST /interview-flows` with the generated questions to get an `interview_flow_id`.
        3.  Call Ribbon's `POST /interviews` with the `interview_flow_id` to get a single-use `interview_link` and `interview_id`.
        4.  Store the `interview_id` and update the `current_state` to `INTERVIEW_PENDING`.
    -   **Response:** `{ "interviewLink": "https://app.ribbon.ai/interview/..." }`

-   **`POST /api/game/{session_id}/check-interview-status`**
    -   **Purpose:** Checks if the pending Ribbon interview is complete, retrieves the transcript, and checks if the game should end.
    -   **Action:**
        1.  Call Ribbon's `GET /interviews` to check the interview status.
        2.  If the interview `status` is "completed":
            -   Append the transcript to the `full_transcript_history` in the database.
            -   **Check End Condition:** Call the LLM with a pre-check prompt ("Do you have enough information to make a final judgment?").
            -   If the LLM answers "yes" OR if `day_number` is 5, trigger the final `end` logic and set the state to the final ending.
            -   If the LLM answers "no," update the `current_state` to the summary step (e.g., "DAY_1_SUMMARY").
    -   **Response:** The updated game state object.

-   **`POST /api/game/{session_id}/next-day`**
    -   **Purpose:** Advances the game from the summary screen to the next day's narrative.
    -   **Action:**
        1.  Increment the `day_number` in the database.
        2.  Update the `current_state` to the next day's intro (e.g., "DAY_2_INTRO").
    -   **Response:** The updated game state object.

-   **`POST /api/game/{session_id}/end`**
    -   **Purpose:** Triggers the final analysis by the LLM to determine the ending.
    -   **Action:**
        1.  Use LangChain to call the LLM with the `full_transcript_history` and a prompt to determine the final judgment.
        2.  Update the `current_state` to reflect the ending (e.g., "ENDING_GUILTY").
    -   **Response:** The final game state object.

### Step 4: LLM Integration (LangChain)

1.  **LLM Configuration:** Initialize an LLM instance (e.g., `ChatOpenAI`) using LangChain.
2.  **Prompt Templates:**
    -   **Initial Prompt:** "You are an interrogator. The subject is accused of assassinating Mayor Elias Vance, a polarizing figure behind the Urban Renewal Project and the Truth Serum Justice System. The subject is a prominent architect whose family home was demolished by Vance's project, and who became a public critic. The subject has amnesia. Generate three vague questions for the first interview, focusing on motive and opportunity."
    -   **Subsequent Prompt:** "Continue the interrogation. Here is the full history of previous interview transcripts: {history}. Reference the evidence and public record from the case of Mayor Vance's assassination (see docs/crime-details.md). Generate three new, more specific questions that probe for inconsistencies or new details."
    -   **Pre-check Prompt:** "Based on the interview history so far: {history}, do you have enough information to make a final judgment of 'guilty', 'innocent', or 'inconclusive'? Respond with only 'yes' or 'no'. If the subject has contradicted established facts from docs/crime-details.md, respond with 'contradiction'."
    -   **Ending Prompt:** "The interrogation is over. Here is the full transcript history: {history}. Based on the evidence and narrative in docs/crime-details.md, determine if the subject is 'guilty', 'innocent', or 'inconclusive'. Respond with only one of these words. If the subject contradicted a known truth, explain which truth was violated and state that the subject is immune to the truth serum and will be executed."

### Step 5: Front-End Implementation (React)

1.  **Game State Components:**
    *   `StartScreen`: Button to call `POST /api/game/start`.
    *   `NarrativeScreen`: Displays story text. Has a button to call `POST /api/game/{session_id}/generate-interview`.
    *   `InterviewScreen`: Displays a loading state and an `<iframe>` whose `src` is set to the `interviewLink` received from the backend. After the iframe is loaded, it will periodically call `POST /api/game/{session_id}/check-interview-status` until the game state changes, indicating the interview is complete.
    *   `DailySummaryScreen`: Displays the transcripts from the last two entries in `full_transcript_history`. Has a "Continue" button that calls `POST /api/game/{session_id}/next-day`.
    *   `EndingScreen`: Displays the final outcome.

2.  **State Management:**
    -   Use a global state manager (e.g., React Context) to hold the `gameState`.
    -   The main `App` component renders the correct screen based on `gameState.currentState`.
    -   Store the `sessionId` in `localStorage` to handle session resumption.

## 4. Recommended Project Structure and Tech Stack


### Backend (`backend/`)
- **Tech Stack:**
  - Python 3.8+
  - Django (web framework)
  - Django REST Framework (API)
  - Django ORM
  - psycopg2-binary (PostgreSQL driver)
  - LangChain (LLM integration)
  - httpx (HTTP client for Ribbon API)
- **Directory Structure:**
  ```
  backend/
  ├── manage.py
  ├── backend/                # Django project root
  │   ├── __init__.py
  │   ├── settings.py         # Django settings
  │   ├── urls.py             # Project URLs
  │   └── wsgi.py/asgi.py     # WSGI/ASGI entrypoints
  ├── gamesession/            # Django app for game logic
  │   ├── __init__.py
  │   ├── models.py           # Django models
  │   ├── serializers.py      # DRF serializers
  │   ├── views.py            # API views
  │   ├── urls.py             # App URLs
  │   └── llm.py/ribbon.py    # LangChain and Ribbon integration
  ├── .env                    # Secrets and DB URL
  ├── requirements.txt
  ```
- **Rationale:**
  - Modular, scalable, and aligns with Django best practices.
  - Built-in admin, migrations, and authentication.
  - Clear separation of models, serializers, views, and integrations.
  - Easy to extend for new features or endpoints.


### Frontend (`frontend/`)
- **Tech Stack:**
  - React (Next.js)
  - Next.js (App Router or Pages Router)
  - Axios (API calls)
  - Zustand or React Context (state management)
  - CSS Modules or styled-components (styling)
- **Directory Structure:**
  ```
  frontend/
  ├── app/ or pages/           # Next.js routing (App Router or Pages Router)
  ├── src/
  │   ├── api/                # API utilities
  │   ├── components/         # Reusable UI components
  │   ├── screens/            # Main game screens (Start, Narrative, Interview, Summary, Ending)
  │   ├── state/              # Global state management
  │   ├── utils/              # Utility functions
  ├── public/
  ├── package.json
  └── next.config.js
  ```
- **Rationale:**
  - Uses Next.js for file-based routing, SSR/SSG, and API routes if needed.
  - Follows modern React and Next.js best practices.
  - Separation of screens and components for clarity.
  - Easy to add new screens or features.

### Monorepo Option
- If desired, a monorepo tool (e.g., pnpm workspaces or turborepo) can be used, but for hackathon speed, two top-level folders is simplest.

---
**Summary:**
- Use `backend/` and `frontend/` at the root.
- Backend: Modular Django app with Django REST Framework, built-in migrations, and clear separation of models, serializers, views, and integrations.
- Frontend: Next.js app with screens, components, and state management, following Next.js conventions.
- All secrets and DB URLs in `.env` (not committed).
