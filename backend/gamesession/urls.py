
from django.urls import path
from . import views

urlpatterns = [
    path('start', views.StartGameView.as_view(), name='start-game'),
    path('<str:session_id>', views.GameSessionDetailView.as_view(), name='game-session-detail'),
    path('<str:session_id>/generate-interview', views.GenerateInterviewView.as_view(), name='generate-interview'),
    path('<str:session_id>/check-interview-status', views.CheckInterviewStatusView.as_view(), name='check-interview-status'),
    path('<str:session_id>/next-day', views.NextDayView.as_view(), name='next-day'),
    path('<str:session_id>/end', views.EndGameView.as_view(), name='end-game'),
    path('ribbon-webhook', views.RibbonWebhookView.as_view(), name='ribbon-webhook'),
]
