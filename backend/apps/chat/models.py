import uuid
from django.db import models
from apps.characters.models import Character
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_room"
    )
    character = models.ForeignKey(
        Character, on_delete=models.PROTECT, related_name="character_room"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Room({self.id}) - {self.user}"


class SenderType(models.TextChoices):
    USER = 'U', 'User'
    AI = 'A', 'AI'


class Chat(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="room_chat"
    )
    content = models.TextField()
    sender_type = models.CharField(max_length=1, choices=SenderType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']