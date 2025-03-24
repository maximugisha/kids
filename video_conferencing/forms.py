# video_conferencing/forms.py
from django import forms
from django.utils import timezone

from .models import ChatMessage, VideoClass


class VideoClassForm(forms.ModelForm):
    class Meta:
        model = VideoClass
        fields = ["title", "description", "scheduled_time", "duration"]
        widgets = {
            "scheduled_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get("scheduled_time")

        if scheduled_time < timezone.now():
            raise forms.ValidationError("Scheduled time cannot be in the past.")

        return scheduled_time


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ["content"]
        widgets = {
            "content": forms.TextInput(
                attrs={
                    "placeholder": "Type your message (use @ai to ask the AI assistant)...",
                    "class": "form-control",
                }
            ),
        }
