# Webhook endpoint for Ribbon interview completion
from rest_framework.views import APIView
# Webhook endpoint for Ribbon interview completion
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

# POST /api/game/ribbon-webhook
@method_decorator(csrf_exempt, name='dispatch')
class RibbonWebhookView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        try:
            # Accept both JSON and form-encoded
            if request.content_type == 'application/json':
                data = request.data
            else:
                data = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            print(f"[WEBHOOK] Failed to parse Ribbon webhook: {e}")
            return Response({"error": "Invalid payload"}, status=400)
        event_type = data.get('event') or data.get('type')
        interview_id = data.get('interview_id')
        print(f"[WEBHOOK] Received event: {event_type} for interview_id: {interview_id}")
        # Only process interview_processed events
        if event_type == 'interview_processed' and interview_id:
            try:
                game = GameSession.objects.get(interview_id=interview_id)
            except GameSession.DoesNotExist:
                print(f"[WEBHOOK] No GameSession found for interview_id {interview_id}")
                return Response({"error": "Session not found"}, status=404)
            # Append transcript if present
            transcript = data.get('transcript')
            if transcript:
                if not isinstance(game.full_transcript_history, list):
                    game.full_transcript_history = []
                game.full_transcript_history.append(transcript)
            # Advance state: set to summary for current day
            game.current_state = f"DAY_{game.day_number}_SUMMARY"
            game.interview_id = None
            game.save()
            print(f"[WEBHOOK] Updated GameSession {game.session_id} to state {game.current_state}")
            return Response({"status": "ok"})
        return Response({"status": "ignored"})

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import GameSession
from .serializers import GameSessionSerializer
import uuid
import os
import sys
import pathlib
import random
import string

# Helper: check if API keys exist
def is_mock_mode():
    # Always try to load .env from backend/.env at process start
    try:
        from dotenv import load_dotenv
        import pathlib
        env_path = pathlib.Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path=env_path, override=False)
    except Exception as e:
        print(f"[DEBUG] Could not load .env: {e}")
    return not (os.environ.get("GEMINI_API_KEY") and os.environ.get("RIBBON_API_KEY"))

def random_session_id():
    return "mock-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

# POST /api/game/start
class StartGameView(APIView):
    def post(self, request):
        if is_mock_mode():
            from django.core.cache import cache
            session_id = random_session_id()
            cache.set(f"mock_day_{session_id}", 1)
            cache.set(f"mock_history_{session_id}", [])
            return Response({"sessionId": session_id})
        session_id = str(uuid.uuid4())
        game = GameSession.objects.create(session_id=session_id, current_state="DAY_1_INTRO", day_number=1)
        return Response({"sessionId": game.session_id})

# GET /api/game/{session_id}
class GameSessionDetailView(APIView):
    def get(self, request, session_id):
        if is_mock_mode():
            from django.core.cache import cache
            day = cache.get(f"mock_day_{session_id}", 1)
            history = cache.get(f"mock_history_{session_id}", [])
            # If game ended, show ending state
            if day == 3:
                current_state = "ENDING_IMMUNE_EXECUTION"
            elif day >= 5:
                current_state = "ENDING_GUILTY"
            else:
                current_state = f"DAY_{day}_INTRO"
            return Response({
                "sessionId": session_id,
                "currentState": current_state,
                "fullTranscriptHistory": history
            })
        try:
            game = GameSession.objects.get(session_id=session_id)
        except GameSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = GameSessionSerializer(game)
        return Response({
            "sessionId": serializer.data["session_id"],
            "currentState": serializer.data["current_state"],
            "fullTranscriptHistory": serializer.data["full_transcript_history"]
        })

# POST /api/game/{session_id}/generate-interview
from . import llm, ribbon

class GenerateInterviewView(APIView):
    def post(self, request, session_id):
        if is_mock_mode():
            from django.core.cache import cache
            day = cache.get(f"mock_day_{session_id}", 1)
            # Set state to INTERVIEW_PENDING
            return Response({"interviewLink": f"https://mock.ribbon.ai/interview/{session_id}-{day}"})
        try:
            game = GameSession.objects.get(session_id=session_id)
        except GameSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        # Generate questions using LLM
        if not game.full_transcript_history:
            questions = llm.generate_questions()
        else:
            questions = llm.generate_questions(history=game.full_transcript_history)
        # Ensure questions is a list of strings
        if isinstance(questions, str):
            questions = [questions]
        elif hasattr(questions, 'content'):
            questions = [questions.content]
        # Flatten any nested lists and filter non-strings
        import logging
        cleaned_questions = []
        logging.info(f"[DEBUG] Raw questions type: {type(questions)} value: {repr(questions)}")
        print(f"[DEBUG] Raw questions type: {type(questions)} value: {repr(questions)}")
        for i, q in enumerate(questions):
            logging.info(f"[DEBUG] Question {i}: type={type(q)}, repr={repr(q)}")
            print(f"[DEBUG] Question {i}: type={type(q)}, repr={repr(q)}")
            if isinstance(q, str):
                q_clean = q.strip()
                # Remove leading/trailing quotes
                q_clean = q_clean.lstrip('"\'').rstrip('"\'').strip()
                # Remove markdown, rationale, or non-question lines
                if not q_clean or 'rationale' in q_clean.lower() or 'here are' in q_clean.lower():
                    continue
                # Only keep lines that end with ?
                if not q_clean.endswith("?"):
                    continue
                cleaned_questions.append(q_clean)
        # If not enough, fallback to any non-empty string
        if len(cleaned_questions) < 3:
            for q in questions:
                if isinstance(q, str):
                    q_clean = q.strip().lstrip('"\'').rstrip('"\'').strip()
                    if q_clean and q_clean not in cleaned_questions:
                        cleaned_questions.append(q_clean)
                    if len(cleaned_questions) >= 3:
                        break
        # Only use up to 3
        questions = cleaned_questions[:3]
        logging.info(f"[DEBUG] Final questions to Ribbon: {questions}")
        print(f"[DEBUG] Final questions to Ribbon: {questions}")
        # Create Ribbon interview flow and interview
        try:
            interview_flow_id = ribbon.create_interview_flow(questions)
            logging.info(f"Ribbon interview_flow_id: {interview_flow_id}")
            print(f"Ribbon interview_flow_id: {interview_flow_id}")
            interview_link, interview_id = ribbon.create_interview(interview_flow_id)
            logging.info(f"Ribbon interview_link: {interview_link}, interview_id: {interview_id}")
            print(f"Ribbon interview_link: {interview_link}, interview_id: {interview_id}")
        except Exception as e:
            # Try to get more info from the exception
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_msg += f" | Ribbon response: {e.response.text}"
                except Exception:
                    pass
            logging.error(f"Ribbon API error in create_interview_flow: {error_msg}")
            print(f"Ribbon API error in create_interview_flow: {error_msg}")
            return Response({"error": f"Ribbon API error in create_interview_flow: {error_msg}"}, status=500)
        # Store interview_id and update state
        game.interview_id = interview_id
        game.current_state = f"DAY_{game.day_number}_INTERVIEW_PENDING"
        game.save()
        return Response({"interviewLink": interview_link})

# POST /api/game/{session_id}/check-interview-status
class CheckInterviewStatusView(APIView):
    def post(self, request, session_id):
        print(f"[DEBUG] CheckInterviewStatusView called for session_id: {session_id}")
        if is_mock_mode():
            from django.core.cache import cache
            key = f"mock_day_{session_id}"
            day = cache.get(key, 1)
            print(f"[MOCK] day: {day}")
            history = cache.get(f"mock_history_{session_id}", [])
            print(f"[MOCK] history: {history}")
            transcript = {"questions": [f"Mock Q{day}A?", f"Mock Q{day}B?", f"Mock Q{day}C?"], "answers": [f"A{day}1", f"A{day}2", f"A{day}3"]}
            print(f"[MOCK] transcript to add: {transcript}")
            history = history + [transcript]
            cache.set(f"mock_history_{session_id}", history)
            if day >= 5:
                precheck_result = "yes"
            elif day == 3:
                precheck_result = "contradiction"
            else:
                precheck_result = "no"
            print(f"[MOCK] LLM precheck for session {session_id}, day {day}: {precheck_result}")
            if precheck_result == "yes":
                current_state = "ENDING_PENDING"
                ending_explanation = None
            elif precheck_result == "contradiction":
                current_state = "ENDING_CONTRADICTION"
                ending_explanation = "The subject contradicted a known truth and is immune to the truth serum. Execution ordered."
            else:
                current_state = f"DAY_{day}_SUMMARY"
                ending_explanation = None
            cache.set(key, day)
            resp = {
                "sessionId": session_id,
                "currentState": current_state,
                "fullTranscriptHistory": history
            }
            if ending_explanation:
                resp["endingExplanation"] = ending_explanation
            print(f"[MOCK] Returning response: {resp}")
            return Response(resp)
        try:
            game = GameSession.objects.get(session_id=session_id)
            print(f"[DEBUG] Loaded GameSession: {game.session_id}, state: {game.current_state}, day: {game.day_number}, interview_id: {game.interview_id}")
        except GameSession.DoesNotExist:
            print(f"[ERROR] GameSession not found for session_id: {session_id}")
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        if not game.interview_id:
            print(f"[DEBUG] No interview in progress for session_id: {session_id}")
            return Response({"error": "No interview in progress"}, status=400)
        try:
            print(f"[DEBUG] Calling ribbon.get_interview_status for interview_id: {game.interview_id}")
            interview_data = ribbon.get_interview_status(game.interview_id)
            print(f"[DEBUG] Ribbon interview_data: {interview_data}")
        except Exception as e:
            print(f"[ERROR] Ribbon API error in CheckInterviewStatus: {str(e)}")
            return Response({"error": f"Ribbon API error in CheckInterviewStatus: {str(e)}"}, status=500)
        status_str = interview_data.get("status")
        print(f"[DEBUG] Ribbon interview status: {status_str}")
        if status_str != "completed":
            print(f"[DEBUG] Interview not completed yet for interview_id: {game.interview_id}")
            return Response({
                "sessionId": game.session_id,
                "currentState": game.current_state,
                "fullTranscriptHistory": game.full_transcript_history
            })
        transcript = interview_data.get("transcript")
        print(f"[DEBUG] Ribbon transcript: {transcript}")
        if transcript:
            history = game.full_transcript_history or []
            print(f"[DEBUG] Appending transcript to history. Before: {history}")
            history.append(transcript)
            game.full_transcript_history = history
            print(f"[DEBUG] After append: {game.full_transcript_history}")
        print(f"[DEBUG] Running LLM precheck with history: {game.full_transcript_history}")
        precheck = llm.get_llm().invoke(llm.PRECHECK_PROMPT.format(history=game.full_transcript_history))
        precheck_result = precheck.content.strip().lower() if hasattr(precheck, 'content') else str(precheck).strip().lower()
        print(f"[LLM] Precheck for session {session_id}: {precheck_result}")
        if precheck_result == "yes" or game.day_number >= 5:
            print(f"[DEBUG] Ending game: precheck_result={precheck_result}, day_number={game.day_number}")
            game.current_state = "ENDING_PENDING"
            ending_explanation = None
        elif precheck_result == "contradiction":
            print(f"[DEBUG] Contradiction detected by LLM.")
            game.current_state = "ENDING_CONTRADICTION"
            ending_explanation = "The subject contradicted a known truth and is immune to the truth serum. Execution ordered."
        else:
            print(f"[DEBUG] Proceeding to summary for day {game.day_number}")
            game.current_state = f"DAY_{game.day_number}_SUMMARY"
            ending_explanation = None
        game.save()
        resp = {
            "sessionId": game.session_id,
            "currentState": game.current_state,
            "fullTranscriptHistory": game.full_transcript_history
        }
        if ending_explanation:
            resp["endingExplanation"] = ending_explanation
        print(f"[DEBUG] Returning response: {resp}")
        return Response(resp)

# POST /api/game/{session_id}/next-day
class NextDayView(APIView):
    def post(self, request, session_id):
        if is_mock_mode():
            from django.core.cache import cache
            key = f"mock_day_{session_id}"
            day = cache.get(key, 1)
            day += 1
            cache.set(key, day)
            # Keep transcript history
            history = cache.get(f"mock_history_{session_id}", [])
            return Response({
                "sessionId": session_id,
                "currentState": f"DAY_{day}_INTRO",
                "fullTranscriptHistory": history
            })
        try:
            game = GameSession.objects.get(session_id=session_id)
        except GameSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        game.day_number += 1
        game.current_state = f"DAY_{game.day_number}_INTRO"
        game.save()
        serializer = GameSessionSerializer(game)
        return Response({
            "sessionId": serializer.data["session_id"],
            "currentState": serializer.data["current_state"],
            "fullTranscriptHistory": serializer.data["full_transcript_history"]
        })

# POST /api/game/{session_id}/end
class EndGameView(APIView):
    def post(self, request, session_id):
        if is_mock_mode():
            from django.core.cache import cache
            day = cache.get(f"mock_day_{session_id}", 1)
            history = cache.get(f"mock_history_{session_id}", [])
            # Simulate ending: day 3 = immune, day 5+ = guilty, else inconclusive
            if day == 3:
                ending = "immune"
                explanation = "The subject contradicted a known truth and is immune to the truth serum. Execution ordered."
                current_state = "ENDING_IMMUNE_EXECUTION"
            elif day >= 5:
                ending = "guilty"
                explanation = "guilty"
                current_state = "ENDING_GUILTY"
            else:
                ending = "inconclusive"
                explanation = "inconclusive"
                current_state = "ENDING_INCONCLUSIVE"
            print(f"[MOCK] LLM ending for session {session_id}, day {day}: {ending}")
            return Response({
                "sessionId": session_id,
                "currentState": current_state,
                "endingExplanation": explanation,
                "fullTranscriptHistory": history
            })
        try:
            game = GameSession.objects.get(session_id=session_id)
        except GameSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        # Call LLM for final judgment
        ending_result = llm.get_llm().invoke(llm.ENDING_PROMPT.format(history=game.full_transcript_history))
        ending = ending_result.content.strip().lower() if hasattr(ending_result, 'content') else str(ending_result).strip().lower()
        print(f"[LLM] Ending for session {session_id}: {ending}")
        # Determine state
        if "guilty" in ending:
            game.current_state = "ENDING_GUILTY"
        elif "innocent" in ending:
            game.current_state = "ENDING_INNOCENT"
        elif "inconclusive" in ending:
            game.current_state = "ENDING_INCONCLUSIVE"
        elif "immune" in ending:
            game.current_state = "ENDING_IMMUNE_EXECUTION"
        else:
            game.current_state = "ENDING_UNKNOWN"
        game.save()
        return Response({
            "sessionId": game.session_id,
            "currentState": game.current_state,
            "endingExplanation": ending,
            "fullTranscriptHistory": game.full_transcript_history
        })
