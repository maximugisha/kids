# video_conferencing/views.py
import json
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ChatMessageForm, VideoClassForm
from .models import ChatMessage, VideoClass


@login_required
def video_class_list(request):
    # Show upcoming classes for the user's organization
    upcoming_classes = VideoClass.objects.filter(
        organization=request.user.organization, scheduled_time__gte=timezone.now()
    ).order_by("scheduled_time")

    # Show past classes
    past_classes = VideoClass.objects.filter(
        organization=request.user.organization, scheduled_time__lt=timezone.now()
    ).order_by("-scheduled_time")[
        :10
    ]  # Show only the 10 most recent past classes

    context = {
        "upcoming_classes": upcoming_classes,
        "past_classes": past_classes,
    }
    return render(request, "video_conferencing/class_list.html", context)


@login_required
def create_video_class(request):
    if not request.user.is_teacher():
        messages.error(request, "Only teachers can create classes.")
        return redirect("video_class_list")

    if request.method == "POST":
        form = VideoClassForm(request.POST)
        if form.is_valid():
            video_class = form.save(commit=False)
            video_class.teacher = request.user
            video_class.organization = request.user.organization
            video_class.room_id = str(uuid.uuid4())[:8]  # Generate a unique room ID
            video_class.save()
            messages.success(request, "Class created successfully!")
            return redirect("video_class_list")
    else:
        form = VideoClassForm()
    return render(request, "video_conferencing/create_class.html", {"form": form})


@login_required
def join_video_class(request, class_id):
    video_class = get_object_or_404(VideoClass, id=class_id)

    # Check if user belongs to the same organization
    if request.user.organization != video_class.organization:
        messages.error(request, "You do not have permission to join this class.")
        return redirect("video_class_list")

    # Check if the class is active or the user is the teacher
    if not video_class.is_active and request.user != video_class.teacher:
        messages.error(request, "This class is not active yet.")
        return redirect("video_class_list")

    # If user is the teacher and class is not active, activate it
    if request.user == video_class.teacher and not video_class.is_active:
        video_class.is_active = True
        video_class.save()

    context = {
        "video_class": video_class,
        "chat_form": ChatMessageForm(),
    }
    return render(request, "video_conferencing/video_room.html", context)


@login_required
def end_video_class(request, class_id):
    video_class = get_object_or_404(VideoClass, id=class_id)

    if request.user != video_class.teacher:
        messages.error(request, "Only the teacher can end the class.")
        return redirect("join_video_class", class_id=video_class.id)

    video_class.is_active = False
    video_class.save()
    messages.success(request, "Class ended successfully!")
    return redirect("video_class_list")


@login_required
def chat_message(request, class_id):
    video_class = get_object_or_404(VideoClass, id=class_id)

    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.video_class = video_class
            message.user = request.user
            message.save()

            # Process message for AI response if it contains "@ai"
            if "@ai" in message.content:
                # Simple AI response - in a real app, you'd integrate with a proper AI service
                ai_content = "I'm the AI assistant. I can help you with your DIY project questions!"
                ChatMessage.objects.create(
                    video_class=video_class, content=ai_content, message_type="ai"
                )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "success"})

            return redirect("join_video_class", class_id=video_class.id)

    return redirect("join_video_class", class_id=video_class.id)


@login_required
def get_chat_messages(request, class_id):
    video_class = get_object_or_404(VideoClass, id=class_id)

    # Get the most recent messages
    messages = ChatMessage.objects.filter(video_class=video_class).order_by(
        "-created_at"
    )[:50]

    messages_data = []
    for message in reversed(list(messages)):  # Reverse to show oldest first
        messages_data.append(
            {
                "id": message.id,
                "content": message.content,
                "user": message.user.username if message.user else "AI Assistant",
                "message_type": message.message_type,
                "timestamp": message.created_at.strftime("%H:%M:%S"),
            }
        )

    return JsonResponse({"messages": messages_data})
