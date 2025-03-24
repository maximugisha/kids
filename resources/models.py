# resources/models.py
from django.db import models

from accounts.models import Organization, User


class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = (
        ("document", "Document"),
        ("presentation", "Presentation"),
        ("video", "Video"),
        ("other", "Other"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="resources/")
    resource_type = models.CharField(max_length=15, choices=RESOURCE_TYPE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resources")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="resources"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
