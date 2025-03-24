# posts/admin.py
from django.contrib import admin

from .models import Comment, Like, Post, Share


class LikeInline(admin.TabularInline):
    model = Like
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("created_at",)


class ShareInline(admin.TabularInline):
    model = Share
    extra = 0
    readonly_fields = ("user", "created_at")
    can_delete = False


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "content_preview",
        "created_at",
        "like_count",
        "comment_count",
        "share_count",
    )
    list_filter = ("created_at",)
    search_fields = ("content", "user__username")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    inlines = [LikeInline, CommentInline, ShareInline]

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"

    def like_count(self, obj):
        return obj.likes.count()

    like_count.short_description = "Likes"

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Comments"

    def share_count(self, obj):
        return obj.shares.count()

    share_count.short_description = "Shares"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post_preview", "content_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "user__username", "post__content")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"

    def post_preview(self, obj):
        return (
            obj.post.content[:30] + "..."
            if len(obj.post.content) > 30
            else obj.post.content
        )

    post_preview.short_description = "Post"


class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__content")
    date_hierarchy = "created_at"

    def post_preview(self, obj):
        return (
            obj.post.content[:30] + "..."
            if len(obj.post.content) > 30
            else obj.post.content
        )

    post_preview.short_description = "Post"


class ShareAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__content")
    date_hierarchy = "created_at"

    def post_preview(self, obj):
        return (
            obj.post.content[:30] + "..."
            if len(obj.post.content) > 30
            else obj.post.content
        )

    post_preview.short_description = "Post"


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Share, ShareAdmin)
