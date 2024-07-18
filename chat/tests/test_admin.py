import json
from unittest.mock import patch

import pytest
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from account.models import CustomUser
from chat.admin import ChatAdmin
from chat.models import Chat, ExternalImage, Message

MOCK_URL_IMAGE = "http://example.com/another_image.jpg"


@pytest.fixture
def admin_user():
    return CustomUser.objects.create_superuser(
        "admin", "admin@example.com", "password"
    )


@pytest.fixture
def chat():
    user = CustomUser.objects.create_user(
        "testuser", "test@example.com", "password"
    )
    return Chat.objects.create(user=user)


@pytest.fixture
def message(chat):
    return Message.objects.create(chat=chat, content="Test message")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "admin_url, model_name, expected_content",
    [
        (
            "admin:chat_chat_changelist",
            "chat",
            lambda chat: chat.user.username,
        ),
        (
            "admin:chat_message_changelist",
            "message",
            lambda message: message.content,
        ),
    ],
)
def test_admin_list_display(
    admin_client, admin_url, model_name, expected_content, request
):
    model = request.getfixturevalue(model_name)
    url = reverse(admin_url)
    response = admin_client.get(url)
    assert response.status_code == 200
    assert expected_content(model) in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "admin_url, model_name, search_field",
    [
        (
            "admin:chat_chat_changelist",
            "chat",
            lambda chat: chat.user.username,
        ),
        (
            "admin:chat_message_changelist",
            "message",
            lambda message: message.content,
        ),
    ],
)
def test_admin_search(
    admin_client, admin_url, model_name, search_field, request
):
    model = request.getfixturevalue(model_name)
    url = reverse(admin_url) + f"?q={search_field(model)}"
    response = admin_client.get(url)
    assert response.status_code == 200
    assert search_field(model) in response.content.decode()


@pytest.mark.django_db
def test_show_send_banner_form(admin_client, admin_user):
    url = reverse("admin:show_send_banner_form")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "Send Banner to All Chats" in response.content.decode()
    assert "<form" in response.content.decode()
    assert 'name="content"' in response.content.decode()
    assert 'type="submit"' in response.content.decode()


@pytest.mark.django_db
def test_message_inline_in_chat_admin(admin_client, chat, message):
    url = reverse("admin:chat_chat_change", args=[chat.id])
    response = admin_client.get(url)
    assert response.status_code == 200
    assert message.content in response.content.decode()


@pytest.mark.django_db
def test_changelist_view(admin_client):
    url = reverse("admin:chat_chat_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "show_send_banners_button" in response.context_data
    assert response.context_data["show_send_banners_button"]


@pytest.mark.django_db
@patch("chat.admin.redis_client")
def test_update_redis_cache(mock_redis):
    ExternalImage.objects.create(
        external_id=12,
        image=SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        ),
        was_sent=False,
    )
    admin_instance = ChatAdmin(ExternalImage, AdminSite())
    admin_instance._update_redis_cache("test_cache_key")
    assert mock_redis.rpush.call_count == 1
    assert mock_redis.expire.called

    calls = mock_redis.rpush.call_args_list
    for call in calls:
        args = call[0]
        assert args[0] == "test_cache_key"
        image_data = json.loads(args[1])
        assert "id" in image_data
        assert "external_id" in image_data
        assert "url" in image_data
        assert "image_path" in image_data


@pytest.mark.django_db
def test_send_banner_to_all_chats_no_image(admin_client):
    url = reverse("admin:process_send_banner_form")
    response = admin_client.post(url, {"content": "Test banner message"})
    assert response.status_code == 302
    assert "No new image available to send in banners" in [
        m.message for m in response.wsgi_request._messages
    ]


@pytest.mark.django_db
@patch("chat.admin.redis_client")
def test_process_send_banner_form_success(mock_redis, admin_client, chat):
    mock_redis.llen.return_value = 5
    image = ExternalImage.objects.create(
        external_id="123",
        image=SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        ),
    )
    url = reverse("admin:process_send_banner_form")
    response = admin_client.post(url, {"content": "Test banner message"})
    assert response.status_code == 302
    assert Message.objects.filter(
        chat=chat, content="Test banner message"
    ).exists()
    image.refresh_from_db()
    assert image.was_sent
    assert Message.objects.count() == 1
    assert "Banners sent successfully." in [
        m.message for m in response.wsgi_request._messages
    ]
    assert mock_redis.llen.called


@pytest.mark.django_db
@patch("chat.admin.redis_client")
@patch("threading.Thread")
def test_process_send_banner_form_update_cache(
    mock_thread, mock_redis, admin_client
):
    ExternalImage.objects.create(
        external_id=12, url="http://test.com", was_sent=False
    )
    mock_redis.llen.return_value = 3
    url = reverse("admin:process_send_banner_form")
    response = admin_client.post(url, {"content": "Test banner"})
    assert response.status_code == 302
    assert mock_thread.called


@pytest.mark.django_db
@patch("chat.admin.Chat.objects.filter")
def test_send_banner_to_all_chats_exception(mock, admin_client):
    mock.side_effect = Exception("Error sending banners")
    ExternalImage.objects.create(
        external_id="1234",
        image=SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        ),
    )
    url = reverse("admin:process_send_banner_form")
    response = admin_client.post(url, {"content": "Test banner message"})
    with pytest.raises(Exception) as excinfo:
        assert response.status_code == 302
        assert "Error sending banners" in excinfo.value.message
