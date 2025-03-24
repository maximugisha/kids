# video_conferencing/admin.py
from django.contrib import admin

from .models import ChatMessage, VideoClass


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("message_type", "user", "content", "created_at")


class VideoClassAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "teacher",
        "organization",
        "scheduled_time",
        "duration",
        "is_active",
    )
    list_filter = ("is_active", "scheduled_time", "organization")
    search_fields = ("title", "description", "teacher__username", "organization__name")
    date_hierarchy = "scheduled_time"
    readonly_fields = ("created_at", "room_id")
    inlines = [ChatMessageInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Regular admins only see classes from their organization
        return qs.filter(organization=request.user.organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization" and not request.user.is_superuser:
            # Limit organization choices to the user's organization
            kwargs["queryset"] = Organization.objects.filter(
                id=request.user.organization.id
            )
        elif db_field.name == "teacher" and not request.user.is_superuser:
            # Limit teacher choices to the teachers from the user's organization
            kwargs["queryset"] = User.objects.filter(
                organization=request.user.organization, user_type="teacher"
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "video_class",
        "user",
        "message_type",
        "content_preview",
        "created_at",
    )
    list_filter = ("message_type", "created_at", "video_class")
    search_fields = ("content", "user__username", "video_class__title")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Regular admins only see messages from their organization
        return qs.filter(video_class__organization=request.user.organization)


admin.site.register(VideoClass, VideoClassAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)

# Fix imports for cross-references between apps
from accounts.models import Organization, User
