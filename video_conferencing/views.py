# video_conferencing/views.py
import json
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .ai_chatbot import AIChatbot
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
def video_room(request, room_id):
    """View for the video classroom"""
    video_class = get_object_or_404(VideoClass, room_id=room_id)

    # Check if the user is allowed to join (teacher or enrolled student)
    if video_class.teacher != request.user and not video_class.students.filter(id=request.user.id).exists():
        # Redirect to enrollment page or show error
        return redirect('enrollment_page')  # Replace with your enrollment URL

    # Update the active status if the teacher is joining
    if video_class.teacher == request.user and not video_class.is_active:
        video_class.is_active = True
        video_class.save()

    # Create chat form
    chat_form = ChatMessageForm()

    context = {
        'video_class': video_class,
        'chat_form': chat_form,
    }

    return render(request, 'video_conferencing/video_room.html', context)


@login_required
@login_required
def chat_message(request, class_id):
    if request.method == 'POST':
        video_class = get_object_or_404(VideoClass, id=class_id)
        content = request.POST.get('content', '')

        if content:
            message_type = 'user'
            if content.startswith('@ai '):
                message_type = 'ai_request'
                clean_message = content.replace('@ai', '').strip()
                context = {
                    'class_title': video_class.title,
                    'user_type': request.user.user_type,
                    'organization': request.user.organization.name
                }
                chatbot = AIChatbot()
                ai_response = chatbot.get_response(clean_message, context)
                ChatMessage.objects.create(
                    video_class=video_class,
                    user=None,  # AI user
                    content=ai_response,
                    message_type='ai'
                )

            ChatMessage.objects.create(
                video_class=video_class,
                user=request.user,
                content=content,
                message_type=message_type
            )

            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def get_chat_messages(request, class_id):
    """Get all chat messages for a class"""
    video_class = get_object_or_404(VideoClass, id=class_id)

    # Get the last 50 messages
    messages = ChatMessage.objects.filter(video_class=video_class).order_by('created_at')[:50]

    messages_data = []
    for msg in messages:
        user_display = 'AI Assistant' if msg.message_type == 'ai' else (msg.user.username if msg.user else 'System')

        messages_data.append({
            'user': user_display,
            'content': msg.content,
            'message_type': msg.message_type,
            'timestamp': msg.created_at.strftime('%H:%M')
        })

    return JsonResponse({'messages': messages_data})


@login_required
def end_video_class(request, class_id):
    """End a video class (teacher only)"""
    if request.method == 'POST':
        video_class = get_object_or_404(VideoClass, id=class_id, teacher=request.user)

        # Mark class as inactive
        video_class.is_active = False
        video_class.end_time = timezone.now()
        video_class.save()

        # Redirect to home or dashboard instead of class summary
        return redirect('class_summary', class_id=class_id)  # Replace 'home' with any existing URL name in your project

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def class_summary(request, class_id):
    """View for class summary after a class has ended"""
    video_class = get_object_or_404(VideoClass, id=class_id)

    # Check if user is authorized to view the summary
    if video_class.teacher != request.user:
        return redirect('home')  # Redirect to home or another appropriate page

    # Get chat messages for this class
    messages = ChatMessage.objects.filter(video_class=video_class).order_by('created_at')

    # Calculate class duration
    duration = video_class.duration

    context = {
        'video_class': video_class,
        'messages': messages,
        'duration': duration,
    }

    return render(request, 'video_conferencing/class_summary.html', context)
