# resources/admin.py
from django.contrib import admin

from .models import Resource


class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "resource_type", "user", "organization", "created_at")
    list_filter = ("resource_type", "organization", "created_at")
    search_fields = ("title", "description", "user__username", "organization__name")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Regular admins only see resources from their organization
        return qs.filter(organization=request.user.organization)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "organization" and not request.user.is_superuser:
            # Limit organization choices to the user's organization
            kwargs["queryset"] = Organization.objects.filter(
                id=request.user.organization.id
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Resource, ResourceAdmin)
