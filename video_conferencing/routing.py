# routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/class/<str:room_id>/', consumers.ClassConsumer.as_asgi()),
]