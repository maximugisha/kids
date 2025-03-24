# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Organization, User


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "description", "logo"]


class UserRegisterForm(UserCreationForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "user_type",
            "organization",
            "profile_picture",
            "bio",
        ]

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")

        if user_type not in ["student", "teacher"]:
            raise forms.ValidationError(
                "User type must be either 'student' or 'teacher'."
            )

        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "profile_picture", "bio"]
