# video_conferencing/ai_chatbot.py
import json
import logging
import os

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AIChatbot:
    """
    A class to handle integration with an external AI service for chatbot functionality.

    This can be integrated with various AI APIs like OpenAI, Anthropic, etc.
    For this example, we'll create a structured class that could work with any of these services.
    """

    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.api_url = "https://api.example.com/v1/chat"  # Replace with actual API URL
        self.context = {}

    def get_response(self, message, user_context=None):
        """
        Get a response from the AI service based on the message and context.

        Args:
            message (str): The user message to respond to
            user_context (dict, optional): Additional context about the user/conversation

        Returns:
            str: The AI response
        """
        if not self.api_key:
            logger.warning("AI API key not configured")
            return self._get_fallback_response(message)

        # Prepare context
        if user_context:
            self.context.update(user_context)

        try:
            # Simplified example - in practice you'd use the specific API's format
            payload = {
                "message": message,
                "context": self.context,
                "type": "educational",
                "audience": "children",  # Important for child-safe responses
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                self.api_url, headers=headers, data=json.dumps(payload), timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                ai_response = result.get("response", "")
                return ai_response
            else:
                logger.error(f"AI API error: {response.status_code} - {response.text}")
                return self._get_fallback_response(message)

        except Exception as e:
            logger.exception(f"Error calling AI service: {str(e)}")
            return self._get_fallback_response(message)

    def _get_fallback_response(self, message):
        """
        Provide a fallback response when the AI service is unavailable.

        Args:
            message (str): The original message

        Returns:
            str: A fallback response
        """
        message = message.lower()

        # Educational DIY project keywords
        if any(word in message for word in ["help", "how", "what should"]):
            return "I'd be happy to help with your DIY project! Can you tell me more about what you're trying to make?"

        elif any(word in message for word in ["idea", "suggest", "recommend"]):
            return "Here are some DIY project ideas: a paper mache volcano, a solar system model, a bird feeder from recycled materials, or a simple robot using cardboard and motors!"

        elif any(word in message for word in ["material", "need", "require"]):
            return "For most DIY projects, you can use recycled materials from home like cardboard boxes, plastic bottles, and paper tubes. Basic supplies include scissors, glue, tape, and markers."

        elif any(word in message for word in ["difficult", "hard", "challenge"]):
            return "It's okay to find parts of your project challenging! That's how we learn. Try breaking it down into smaller steps or ask your teacher for specific guidance."

        elif any(word in message for word in ["thank", "thanks"]):
            return "You're welcome! I'm always here to help with your DIY projects. Good luck and have fun creating!"

        else:
            return "That's an interesting question about your DIY project! If you need help with something specific, try asking your teacher or check out the resources section for guides and materials."


# To use this class in views.py:
"""
from .ai_chatbot import AIChatbot

def generate_ai_response(message, video_class, user):
    # Clean the message (remove @ai, etc.)
    clean_message = message.replace('@ai', '').strip()
    
    # Create context for the AI
    context = {
        'class_title': video_class.title,
        'user_type': user.user_type,
        'organization': user.organization.name
    }
    
    # Get AI response
    chatbot = AIChatbot()
    response = chatbot.get_response(clean_message, context)
    
    return response
"""
