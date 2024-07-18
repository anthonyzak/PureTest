import pytest
from django.contrib import admin
from django.test import RequestFactory

from chat.models import Chat
from utils.admin_actions import delete_chats


@pytest.fixture
def chat_instances(admin_user):
    return [
        Chat.objects.create(user=admin_user, is_deleted=False)
        for _ in range(3)
    ]


@pytest.mark.django_db
@pytest.mark.parametrize("num_selected", [1, 2, 3])
def test_delete_chats(admin_user, chat_instances, num_selected):
    factory = RequestFactory()
    request = factory.get("/")
    request.user = admin_user

    queryset = Chat.objects.filter(
        id__in=[chat.id for chat in chat_instances[:num_selected]]
    )

    delete_chats(admin.ModelAdmin(Chat, admin.site), request, queryset)

    for chat in chat_instances[:num_selected]:
        chat.refresh_from_db()
        assert chat.is_deleted

    for chat in chat_instances[num_selected:]:
        chat.refresh_from_db()
        assert not chat.is_deleted
