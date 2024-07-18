import json
import logging
import threading
from typing import Any, Dict, List, Optional

import redis
from django.contrib import admin, messages
from django.contrib.auth.decorators import user_passes_test
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import redirect, render
from django.urls import path
from django_celery_beat.models import (
    ClockedSchedule,
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
    SolarSchedule,
)

from chat.forms import BannerMessageForm
from chat.models import Chat, ExternalImage, Message
from core.settings import BULK_CREATE_BATCH_SIZE, REDIS_HOST, REDIS_PORT
from utils.admin_actions import delete_elements
from utils.permissions import (
    has_modify_permissions,
    has_modify_permissions_for_module,
)
from utils.redis import cache_decorator

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
logger = logging.getLogger(__name__)


class MessageInline(admin.TabularInline):
    """
    Inline admin descriptor for Message model.
    """

    model = Message
    fields = ["content", "image"]
    extra = 1
    max_num = 20


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """
    Admin view for the Chat model.
    """

    change_list_template = "admin/chat_changelist.html"
    list_display = ("id", "user", "created_at", "updated_at", "is_deleted")
    search_fields = ("user__username", "user__email")
    list_filter = ("user__username", "is_deleted", "created_at", "updated_at")
    list_select_related = ("user",)
    raw_id_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    exclude = ("deleted_at", "is_deleted")
    actions = [delete_elements]
    inlines = [MessageInline]

    def get_queryset(self, request):
        """
        Get the queryset for the admin view.

        :param request: The current request object.
        :return: The queryset with related user objects.
        """
        return super().get_queryset(request).select_related("user")

    def get_urls(self) -> List[str]:
        """
        Get the custom URLs for the admin view.

        :return: List of custom URLs.
        """
        urls = super().get_urls()
        custom_urls = [
            path(
                "send_banners/",
                user_passes_test(
                    has_modify_permissions_for_module("chat", "message")
                )(self.show_send_banner_form),
                name="show_send_banner_form",
            ),
            path(
                "process_send_banners/",
                user_passes_test(
                    has_modify_permissions_for_module("chat", "message")
                )(
                    lambda request: self.process_send_banner_form(
                        request, cache_key="available_banner_images"
                    )
                ),
                name="process_send_banner_form",
            ),
        ]
        return custom_urls + urls

    def show_send_banner_form(self, request):
        """
        Show the form to send a banner message to all chats.

        :param request: The current request object.
        :return: Rendered form for sending banner messages.
        """
        form = BannerMessageForm()
        context = {
            "form": form,
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(request),
            "site_header": "Django administration",
            "title": "Send Banner to All Chats",
        }
        return render(request, "admin/send_banners_form.html", context)

    def _update_redis_cache(self, cache_key: str) -> None:
        """
        Update the Redis cache with available images.

        :param cache_key: Key for the Redis cache.
        """
        CACHE_SIZE = 30

        available_images = ExternalImage.objects.filter(
            was_sent=False
        ).order_by("external_id")[:CACHE_SIZE]

        for image in available_images:
            image_data = {
                "id": str(image.id),
                "external_id": image.external_id,
                "url": image.url,
                "image_path": image.image.name if image.image else None,
            }
            redis_client.rpush(
                cache_key, json.dumps(image_data, cls=DjangoJSONEncoder)
            )

        redis_client.expire(cache_key, 3600)

    @cache_decorator()
    def process_send_banner_form(
        self, request, image_data: Optional[Dict[str, Any]], cache_key: str
    ):
        """
        Process the form to send a banner message to all chats.

        :param request: The current request object.
        :param image_data: Optional dictionary containing image data.
        :param cache_key: Key for the Redis cache.
        :return: Redirect response to the admin change list view.
        """
        if not image_data:
            image = (
                ExternalImage.objects.filter(was_sent=False)
                .order_by("external_id")
                .first()
            )
            if not image:
                self.message_user(
                    request,
                    "No new image available to send in banners",
                    level=messages.WARNING,
                )
                return redirect("..")
            image_data = {
                "id": str(image.id),
                "image_path": image.image.name if image.image else None,
            }
        if request.method == "POST":
            form = BannerMessageForm(request.POST)
            if form.is_valid():
                content = form.cleaned_data["content"]
                try:
                    chats = Chat.objects.filter(is_deleted=False)

                    messages_to_create = [
                        Message(
                            chat=chat,
                            content=content,
                            image=image_data.get("image_path"),
                        )
                        for chat in chats
                    ]

                    Message.objects.bulk_create(
                        messages_to_create, batch_size=BULK_CREATE_BATCH_SIZE
                    )

                    ExternalImage.objects.filter(id=image_data["id"]).update(
                        was_sent=True
                    )

                    cached_images_count = redis_client.llen(cache_key)
                    if cached_images_count < 5:
                        threading.Thread(
                            target=self._update_redis_cache, args=(cache_key,)
                        ).start()
                    self.message_user(
                        request,
                        "Banners sent successfully.",
                        level=messages.SUCCESS,
                    )

                except Exception as e:
                    logger.error(
                        f"Error performing send banner action. Error: {str(e)}"
                    )
                    self.message_user(
                        request, "Error sending banners", level=messages.ERROR
                    )

        return redirect("..")

    def changelist_view(
        self, request, extra_context: Optional[Dict[str, Any]] = None
    ):
        """
        Customize the change list view to include the send banners button.

        :param request: The current request object.
        :param extra_context: Additional context for the change list view.
        :return: Rendered change list view.
        """
        extra_context = extra_context or {}
        extra_context["show_send_banners_button"] = has_modify_permissions(
            request.user, "chat", "message"
        )
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin view for the Message model.
    """

    list_display = (
        "id",
        "display_user",
        "content",
        "created_at",
        "updated_at",
        "is_deleted",
    )
    list_select_related = ("chat", "chat__user")
    search_fields = ("chat__user__username", "chat__user__email", "content")
    list_filter = (
        "chat__user__username",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    raw_id_fields = ("chat",)
    readonly_fields = ("created_at", "updated_at")
    exclude = ("deleted_at", "is_deleted")
    actions = [delete_elements]

    def get_queryset(self, request):
        """
        Get the queryset for the admin view.

        :param request: The current request object.
        :return: The queryset with related chat and user objects.
        """
        return (
            super().get_queryset(request).select_related("chat", "chat__user")
        )

    def display_user(self, obj):
        """
        Display the username of the user associated with the message.

        :param obj: The Message instance.
        :return: The username of the associated user.
        """
        return obj.chat.user.username

    display_user.short_description = "User"


# Unregister tasks views
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.disable_action("delete_selected")
