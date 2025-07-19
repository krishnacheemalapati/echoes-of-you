
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import GameSession
from .serializers import GameSessionSerializer
import uuid
import os

# Helper: check if API keys exist
def is_mock_mode():
    return not (os.environ.get("LLM_API_KEY") and os.environ.get("RIBBON_API_KEY"))

# POST /api/game/start
class StartGameView(APIView):
    def post(self, request):
        if is_mock_mode():
            session_id = "mock-session-1234"
            return Response({"sessionId": session_id})
        session_id = str(uuid.uuid4())
        game = GameSession.objects.create(session_id=session_id, current_state="DAY_1_INTRO", day_number=1)
        return Response({"sessionId": game.session_id})

# GET /api/game/{session_id}
class GameSessionDetailView(APIView):
    def get(self, request, session_id):
        if is_mock_mode():
            return Response({
                "sessionId": session_id,
                "currentState": "DAY_1_INTRO",
                "fullTranscriptHistory": []
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
            return Response({"interviewLink": "https://mock.ribbon.ai/interview/mock-interview-1234"})
        try:
            game = GameSession.objects.get(session_id=session_id)
        except GameSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        # Generate questions using LLM
        if not game.full_transcript_history:
            questions = llm.generate_questions()
        else:
            questions = llm.generate_questions(history=game.full_transcript_history)
        # If LLM returns a string, wrap in list
        if isinstance(questions, str):
            questions = [questions]
        elif hasattr(questions, 'content'):
            questions = [questions.content]
        # Create Ribbon interview flow and interview
        try:
            interview_flow_id = ribbon.create_interview_flow(questions)
            interview_link, interview_id = ribbon.create_interview(interview_flow_id)
        except Exception as e:
            return Response({"error": f"Ribbon API error: {str(e)}"}, status=500)
        # Store interview_id and update state
        game.interview_id = interview_id
        game.current_state = f"DAY_{game.day_number}_INTERVIEW_PENDING"
        game.save()
        return Response({"interviewLink": interview_link})

# POST /api/game/{session_id}/check-interview-status
class CheckInterviewStatusView(APIView):
    def post(self, request, session_id):
        if is_mock_mode():
            # Use a session-based counter to simulate day progression
            from django.core.cache import cache
            key = f"mock_day_{session_id}"
            day = cache.get(key, 1)
            # Simulate transcript history
            history = cache.get(f"mock_history_{session_id}", [])
            transcript = {"questions": [f"Mock Q{day}A?", f"Mock Q{day}B?", f"Mock Q{day}C?"], "answers": [f"A{day}1", f"A{day}2", f"A{day}3"]}
            history = history + [transcript]
            cache.set(f"mock_history_{session_id}", history)
            # Simulate LLM precheck: day 5 or more = yes, day 3 = contradiction, else no
            if day >= 5:
                precheck_result = "yes"
            elif day == 3:
                precheck_result = "contradiction"
            else:
                precheck_result = "no"
            print(f"[MOCK] LLM precheck for session {session_id}, day {day}: {precheck_result}")
            if precheck_result == "yes":
                current_state = "ENDING_PENDING"
            elif precheck_result == "contradiction":
                current_state = "ENDING_CONTRADICTION"
            else:
                current_state = f"DAY_{day}_SUMMARY"
            cache.set(key, day)  # Save current day
            return Response({
                "sessionId": session_id,
                "currentState": current_state,
                "fullTranscriptHistory": history
            })
        try:
            game = GameSession.objects.get(session_id=session_id)
        except GameSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        if not game.interview_id:
            return Response({"error": "No interview in progress"}, status=400)
        # Check Ribbon interview status
        try:
            interview_data = ribbon.get_interview_status(game.interview_id)
        except Exception as e:
            return Response({"error": f"Ribbon API error: {str(e)}"}, status=500)
        status_str = interview_data.get("status")
        if status_str != "completed":
            # Still pending
            return Response({
                "sessionId": game.session_id,
                "currentState": game.current_state,
                "fullTranscriptHistory": game.full_transcript_history
            })
        # Interview completed: get transcript
        transcript = interview_data.get("transcript")
        if transcript:
            history = game.full_transcript_history or []
            history.append(transcript)
            game.full_transcript_history = history
        # LLM pre-check: should we end?
        precheck = llm.get_llm().invoke(llm.PRECHECK_PROMPT.format(history=game.full_transcript_history))
        precheck_result = precheck.content.strip().lower() if hasattr(precheck, 'content') else str(precheck).strip().lower()
        print(f"[LLM] Precheck for session {session_id}: {precheck_result}")
        if precheck_result == "yes" or game.day_number >= 5:
            # End game
            game.current_state = "ENDING_PENDING"
        elif precheck_result == "contradiction":
            game.current_state = "ENDING_CONTRADICTION"
        else:
            game.current_state = f"DAY_{game.day_number}_SUMMARY"
        game.save()
        return Response({
            "sessionId": game.session_id,
            "currentState": game.current_state,
            "fullTranscriptHistory": game.full_transcript_history
        })

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
