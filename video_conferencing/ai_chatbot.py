import json
import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)


class AIChatbot:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.context = {}
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def get_response(self, message, user_context=None):
        if not self.api_key:
            logger.warning("Google API key not configured")
            return self._get_fallback_response(message)

        if user_context:
            self.context.update(user_context)

        try:
            prompt = self._build_prompt(message)
            response = self.model.generate_content(prompt)
            ai_response = response.text.strip()
            return ai_response

        except Exception as e:
            logger.exception(f"Error calling Google Gemini service: {str(e)}")
            return self._get_fallback_response(message)

    def _build_prompt(self, message):
        try:
            context_json = json.dumps(self.context)
        except TypeError as e:
            logger.error(f"Error serializing context: {str(e)}")
            context_json = "{}"
        prompt = f"User message: {message}\nContext: {context_json}\nResponse:"
        return prompt

    def _get_fallback_response(self, message):
        message = message.lower()
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
