
from django.db import models
import uuid


class GameSession(models.Model):
    session_id = models.CharField(primary_key=True, max_length=64, default=uuid.uuid4, editable=False)
    current_state = models.CharField(max_length=64)
    day_number = models.IntegerField(default=1)
    full_transcript_history = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    interview_id = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return f"Session {self.session_id} (Day {self.day_number})"
