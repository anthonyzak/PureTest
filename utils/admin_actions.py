from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest


@admin.action(
    permissions=["delete"],
    description="Delete selected elements",
)
def delete_elements(
    model_admin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet
) -> None:
    """
    Marks the selected instances as deleted. Soft delete.

    :param model_admin: The current ModelAdmin instance.
    :param request: The current HttpRequest instance.
    :param queryset: The QuerySet of chat instances
        selected in the admin interface.
    """
    queryset.update(is_deleted=True)
