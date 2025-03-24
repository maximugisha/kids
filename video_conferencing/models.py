# video_conferencing/models.py
from django.db import models

from accounts.models import Organization, User


class VideoClass(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_classes"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="classes"
    )
    room_id = models.CharField(max_length=50, unique=True)
    scheduled_time = models.DateTimeField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = (
        ("user", "User Message"),
        ("ai", "AI Message"),
    )

    video_class = models.ForeignKey(
        VideoClass, on_delete=models.CASCADE, related_name="chat_messages"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages",
        null=True,
        blank=True,
    )
    content = models.TextField()
    message_type = models.CharField(
        max_length=10, choices=MESSAGE_TYPE_CHOICES, default="user"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.video_class.title} by {'AI' if self.message_type == 'ai' else self.user.username}"
