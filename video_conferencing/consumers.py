# video_conferencing/consumers.py
import json
import uuid

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from accounts.models import User

from .models import ChatMessage, VideoClass


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.class_id = self.scope["url_route"]["kwargs"]["class_id"]
        self.room_group_name = f"chat_{self.class_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user_id = data["user_id"]

        # Save the message to the database
        await self.save_message(user_id, message)

        # Check if the message is directed to AI
        if "@ai" in message:
            # Generate AI response
            ai_response = await self.generate_ai_response(message)

            # Save AI response
            await self.save_ai_message(ai_response)

            # Send AI message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": ai_response,
                    "user": "AI Assistant",
                    "message_type": "ai",
                    "timestamp": self.get_timestamp(),
                },
            )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user_id": user_id,
                "message_type": "user",
                "timestamp": self.get_timestamp(),
            },
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        message_type = event["message_type"]
        timestamp = event["timestamp"]

        if message_type == "user":
            user_id = event["user_id"]
            user = await self.get_user(user_id)
            username = user.username
        else:
            username = "AI Assistant"

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "user": username,
                    "message_type": message_type,
                    "timestamp": timestamp,
                }
            )
        )

    @database_sync_to_async
    def save_message(self, user_id, message):
        user = User.objects.get(id=user_id)
        video_class = VideoClass.objects.get(id=self.class_id)
        ChatMessage.objects.create(
            video_class=video_class, user=user, content=message, message_type="user"
        )

    @database_sync_to_async
    def save_ai_message(self, message):
        video_class = VideoClass.objects.get(id=self.class_id)
        ChatMessage.objects.create(
            video_class=video_class, content=message, message_type="ai"
        )

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    def get_timestamp(self):
        from django.utils import timezone

        return timezone.now().strftime("%H:%M:%S")

    async def generate_ai_response(self, message):
        # In a real implementation, you would call an AI API here
        # For now, we'll use a simple mock response
        message = message.replace("@ai", "").strip()

        # Simple keyword-based responses
        if "help" in message.lower():
            return "I'm here to help with your DIY project! What are you making?"
        elif "idea" in message.lower() or "suggestion" in message.lower():
            return "Here are some DIY project ideas: a homemade volcano, a solar system model, a bird feeder, or a simple robot!"
        elif "material" in message.lower():
            return "For most DIY projects, you can use recycled materials like cardboard boxes, plastic bottles, and paper tubes. Common supplies include scissors, glue, tape, and markers."
        else:
            return "That's an interesting DIY question! I suggest exploring more about this topic on the resources page where teachers have shared helpful guides."
