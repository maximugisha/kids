# resources/forms.py
from django import forms

from .models import Resource


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["title", "description", "file", "resource_type"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
