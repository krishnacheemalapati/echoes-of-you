
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import GameSession
from .serializers import GameSessionSerializer
import uuid

# POST /api/game/start
class StartGameView(APIView):
    def post(self, request):
        session_id = str(uuid.uuid4())
        game = GameSession.objects.create(session_id=session_id, current_state="DAY_1_INTRO", day_number=1)
        return Response({"sessionId": game.session_id})

# GET /api/game/{session_id}
class GameSessionDetailView(APIView):
    def get(self, request, session_id):
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
        try:
            game = GameSession.objects.get(session_id=session_id)
        except GameSession.DoesNotExist:
            return Response({"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND)
        # Call LLM for final judgment
        ending_result = llm.get_llm().invoke(llm.ENDING_PROMPT.format(history=game.full_transcript_history))
        ending = ending_result.content.strip().lower() if hasattr(ending_result, 'content') else str(ending_result).strip().lower()
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
