# video_conferencing/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.video_class_list, name="video_class_list"),
    path("create/", views.create_video_class, name="create_video_class"),
    path("<int:class_id>/join/", views.join_video_class, name="join_video_class"),
    path("<int:class_id>/end/", views.end_video_class, name="end_video_class"),
    path("<int:class_id>/chat/", views.chat_message, name="chat_message"),
    path(
        "<int:class_id>/chat/messages/",
        views.get_chat_messages,
        name="get_chat_messages",
    ),
    path("<int:class_id>/join/", views.join_video_class, name="join_video_class"),
    path('<int:class_id>/summary/', views.class_summary, name='class_summary'),

]
