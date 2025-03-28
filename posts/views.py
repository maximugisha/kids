# posts/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Follow, User

from .forms import CommentForm, PostForm
from .models import Comment, Like, Post, Share

@login_required
def home(request):
    # Get posts from users that the current user follows
    following_users = Follow.objects.filter(follower=request.user).values_list(
        "following", flat=True
    )
    posts = Post.objects.filter(user__in=following_users).order_by("-created_at")

    # Include the user's own posts
    user_posts = Post.objects.filter(user=request.user).order_by("-created_at")

    # Combine and sort all posts
    all_posts = list(posts) + list(user_posts)
    # all_posts.sort(key=lambda x: x.created_at, reverse=True)

    # Get suggested users (users that the current user is not following)
    suggested_users = User.objects.exclude(id__in=following_users).exclude(id=request.user.id)

    context = {
        "posts": all_posts,
        "form": PostForm(),
        "suggested_users": suggested_users,
    }
    return render(request, "posts/home.html", context)


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect("home")
    else:
        form = PostForm()
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by("-created_at")

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, "Comment added successfully!")
            return redirect("post_detail", post_id=post.id)
    else:
        comment_form = CommentForm()

    context = {
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
        "user_liked": post.likes.filter(user=request.user).exists(),
        "user_shared": post.shares.filter(user=request.user).exists(),
    }

    return render(request, "posts/post_detail.html", context)


@login_required
def like_toggle(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_exists = Like.objects.filter(user=request.user, post=post).exists()

    if like_exists:
        Like.objects.filter(user=request.user, post=post).delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "liked": liked,
                "like_count": post.likes.count(),
            }
        )
    else:
        return redirect("post_detail", post_id=post.id)


@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Check if already shared
    if not Share.objects.filter(user=request.user, post=post).exists():
        Share.objects.create(user=request.user, post=post)
        messages.success(request, "Post shared successfully!")
    else:
        messages.info(request, "You have already shared this post.")

    return redirect("post_detail", post_id=post.id)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        messages.error(request, "You cannot delete someone else's post.")
        return redirect("post_detail", post_id=post.id)

    post.delete()
    messages.success(request, "Post deleted successfully!")
    return redirect("home")
