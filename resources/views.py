# resources/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ResourceForm
from .models import Resource


@login_required
def resource_list(request):
    # Filter resources by user's organization
    resources = Resource.objects.filter(
        organization=request.user.organization
    ).order_by("-created_at")

    context = {
        "resources": resources,
    }
    return render(request, "resources/resource_list.html", context)


@login_required
def create_resource(request):
    if not request.user.is_teacher():
        messages.error(request, "Only teachers can upload resources.")
        return redirect("resource_list")

    if request.method == "POST":
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.organization = request.user.organization
            resource.save()
            messages.success(request, "Resource uploaded successfully!")
            return redirect("resource_list")
    else:
        form = ResourceForm()
    return render(request, "resources/create_resource.html", {"form": form})


@login_required
def download_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)

    # Check if user belongs to the same organization
    if request.user.organization != resource.organization:
        messages.error(request, "You do not have permission to download this resource.")
        return redirect("resource_list")

    response = HttpResponse(resource.file, content_type="application/force-download")
    response["Content-Disposition"] = f'attachment; filename="{resource.file.name}"'
    return response


@login_required
def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)

    # Check if user is the uploader or admin
    if resource.user != request.user and not request.user.is_superuser:
        messages.error(request, "You do not have permission to delete this resource.")
        return redirect("resource_list")

    resource.delete()
    messages.success(request, "Resource deleted successfully!")
    return redirect("resource_list")
