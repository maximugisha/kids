# kids_diy/asgi.py
import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kids_diy.settings")

# Initialize Django before importing modules that depend on it
django.setup()

# Import after django.setup()
import video_conferencing.routing

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(video_conferencing.routing.websocket_urlpatterns)
        ),
    }
)
