
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import GameSession

from unittest.mock import patch

class GameSessionAPITests(APITestCase):
    def test_start_game(self):
        url = reverse('start-game')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('sessionId', response.data)
        session_id = response.data['sessionId']
        self.assertTrue(GameSession.objects.filter(session_id=session_id).exists())

    def test_game_session_detail(self):
        game = GameSession.objects.create(session_id='test123', current_state='DAY_1_INTRO', day_number=1)
        url = reverse('game-session-detail', args=['test123'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['sessionId'], 'test123')

    def test_next_day(self):
        game = GameSession.objects.create(session_id='test456', current_state='DAY_1_SUMMARY', day_number=1)
        url = reverse('next-day', args=['test456'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['currentState'], 'DAY_2_INTRO')
        game.refresh_from_db()
        self.assertEqual(game.day_number, 2)

    @patch('gamesession.llm.get_llm')
    def test_end_game(self, mock_llm):
        # Patch LLM to return 'guilty' for deterministic test
        mock_llm.return_value.invoke.return_value.content = 'guilty'
        game = GameSession.objects.create(session_id='test789', current_state='DAY_1_SUMMARY', day_number=1)
        url = reverse('end-game', args=['test789'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['currentState'], 'ENDING_GUILTY')

    @patch('gamesession.llm.generate_questions')
    @patch('gamesession.ribbon.create_interview_flow')
    @patch('gamesession.ribbon.create_interview')
    def test_generate_interview(self, mock_create_interview, mock_create_flow, mock_generate_questions):
        # Setup mocks
        mock_generate_questions.return_value = ["Q1?", "Q2?", "Q3?"]
        mock_create_flow.return_value = "flow123"
        mock_create_interview.return_value = ("https://app.ribbon.ai/interview/mock", "interview123")
        game = GameSession.objects.create(session_id='testgen', current_state='DAY_1_INTRO', day_number=1)
        url = reverse('generate-interview', args=['testgen'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('interviewLink', response.data)
        game.refresh_from_db()
        self.assertEqual(game.interview_id, "interview123")
        self.assertEqual(game.current_state, "DAY_1_INTERVIEW_PENDING")

    @patch('gamesession.llm.get_llm')
    @patch('gamesession.ribbon.get_interview_status')
    def test_check_interview_status(self, mock_get_interview_status, mock_get_llm):
        # Setup mocks
        mock_get_interview_status.return_value = {"status": "completed", "transcript": {"q": "a"}}
        mock_get_llm.return_value.invoke.return_value.content = 'no'
        game = GameSession.objects.create(session_id='testchk', current_state='DAY_1_INTERVIEW_PENDING', day_number=1, interview_id='intv123', full_transcript_history=[])
        url = reverse('check-interview-status', args=['testchk'])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['currentState'], 'DAY_1_SUMMARY')
        self.assertEqual(len(response.data['fullTranscriptHistory']), 1)
