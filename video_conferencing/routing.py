# video_conferencing/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/class/(?P<class_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
