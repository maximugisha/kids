# resources/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path("", views.resource_list, name="resource_list"),
    path("create/", views.create_resource, name="create_resource"),
    path(
        "<int:resource_id>/download/", views.download_resource, name="download_resource"
    ),
    path("<int:resource_id>/delete/", views.delete_resource, name="delete_resource"),
]
