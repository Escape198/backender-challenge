from django.db import models


class OutboxEvent(models.Model):
    user_id = models.UUIDField()
    event_data = models.JSONField()
    status = models.CharField(max_length=50, default='pending')  # pending или processed
    created_at = models.DateTimeField(auto_now_add=True)
