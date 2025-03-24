# posts/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("post/create/", views.create_post, name="create_post"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("post/<int:post_id>/like/", views.like_toggle, name="like_toggle"),
    path("post/<int:post_id>/share/", views.share_post, name="share_post"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete_post"),
]
