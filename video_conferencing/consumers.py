# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import VideoClass, ChatMessage
from .ai_chatbot import AIChatbot

class ClassConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'class_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Store connected peers for this room
        if not hasattr(self, 'room_peers'):
            self.room_peers = set()

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # Handle different message types
        if 'type' in data:
            message_type = data['type']

            if message_type == 'chat':
                # Regular chat message
                message = data['message']
                user_id = data['user_id']

                # Check for AI assistant trigger (@ai)
                if message.startswith('@ai '):
                    ai_message = message[4:]  # Remove the '@ai ' part
                    await self.save_chat_message(user_id, message, 'user')

                    # Generate AI response
                    ai_response = await self.generate_ai_response(ai_message)

                    # Save and broadcast AI message
                    await self.save_chat_message('ai', ai_response, 'ai')

                    timestamp = timezone.now().strftime('%H:%M')

                    # Send AI message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'user': 'AI Assistant',
                            'message': ai_response,
                            'message_type': 'ai',
                            'timestamp': timestamp
                        }
                    )
                else:
                    # Regular user message
                    await self.save_chat_message(user_id, message, 'user')

                    user = await self.get_user(user_id)
                    timestamp = timezone.now().strftime('%H:%M')

                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'user': user.username,
                            'message': message,
                            'message_type': 'user',
                            'timestamp': timestamp
                        }
                    )

            elif message_type == 'hand_raise':
                # Hand raise notification
                user_id = data['user_id']
                username = data['username']
                raised = data['raised']

                # Send hand raise notification to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'hand_raise',
                        'user_id': user_id,
                        'username': username,
                        'raised': raised
                    }
                )

            elif message_type == 'join':
                # User joined - track their peer ID
                user_id = data['user_id']
                username = data['username']
                peer_id = data['peer_id']

                # Add to list of room peers
                if not hasattr(self.__class__, 'room_peers'):
                    self.__class__.room_peers = {}

                if self.room_id not in self.__class__.room_peers:
                    self.__class__.room_peers[self.room_id] = set()

                self.__class__.room_peers[self.room_id].add(peer_id)

                # Broadcast join message to all users
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_joined',
                        'user_id': user_id,
                        'username': username,
                        'peer_id': peer_id
                    }
                )

            elif message_type == 'leave':
                # User left
                user_id = data['user_id']
                username = data['username']
                peer_id = data.get('peer_id', '')

                # Remove from list of room peers
                if hasattr(self.__class__, 'room_peers') and self.room_id in self.__class__.room_peers:
                    if peer_id in self.__class__.room_peers[self.room_id]:
                        self.__class__.room_peers[self.room_id].remove(peer_id)

                # Broadcast leave message
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_left',
                        'user_id': user_id,
                        'username': username,
                        'peer_id': peer_id
                    }
                )

            elif message_type == 'get_users':
                # User is requesting list of existing users
                if hasattr(self.__class__, 'room_peers') and self.room_id in self.__class__.room_peers:
                    peer_list = list(self.__class__.room_peers[self.room_id])

                    # Send back list of users
                    await self.send(text_data=json.dumps({
                        'type': 'user_list',
                        'users': peer_list
                    }))

    # Handlers for different message types
    async def chat_message(self, event):
        # Send chat message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'user': event['user'],
            'message': event['message'],
            'message_type': event['message_type'],
            'timestamp': event['timestamp']
        }))

    async def hand_raise(self, event):
        # Send hand raise notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'hand_raise',
            'user_id': event['user_id'],
            'username': event['username'],
            'raised': event['raised']
        }))

    async def user_joined(self, event):
        # Send user joined notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'join',
            'user_id': event['user_id'],
            'username': event['username'],
            'peer_id': event['peer_id']
        }))

    async def user_left(self, event):
        # Send user left notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'leave',
            'user_id': event['user_id'],
            'username': event['username'],
            'peer_id': event['peer_id']
        }))

    @database_sync_to_async
    def save_chat_message(self, user_id, message, message_type):
        """Save a chat message to the database"""
        video_class = VideoClass.objects.get(id=self.room_id)

        # If it's a system or AI message
        if user_id == 'system' or user_id == 'ai':
            ChatMessage.objects.create(
                video_class=video_class,
                content=message,
                message_type=message_type
            )
            return

        # Regular user message
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)

            ChatMessage.objects.create(
                video_class=video_class,
                user=user,
                content=message,
                message_type=message_type
            )
        except Exception as e:
            print(f"Error saving message: {e}")

    @database_sync_to_async
    def get_user(self, user_id):
        """Get user object from user_id"""
        if user_id == 'system' or user_id == 'ai':
            return type('obj', (object,), {'username': 'System' if user_id == 'system' else 'AI Assistant'})

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.get(id=user_id)
        except Exception as e:
            print(f"Error getting user: {e}")
            return type('obj', (object,), {'username': 'Unknown User'})

    @database_sync_to_async
    def generate_ai_response(self, message):
        clean_message = message.replace('@ai', '').strip()
        context = {

        }
        chatbot = AIChatbot()
        response = chatbot.get_response(clean_message, context)
        return response