import uuid
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from account.models import CustomUser
from chat.models import Chat, ExternalImage, Message

URL_IMAGE = "https://api.slingacademy.com/public/sample-photos/1.jpeg"
MOCK_URL_IMAGE_1 = "http://example.com/another_image.jpg"
MOCK_URL_IMAGE_2 = "http://example.com/new_image.jpg"


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def chat(user):
    return Chat.objects.create(user=user)


@pytest.fixture
def external_image():
    return ExternalImage.objects.create(external_id=1, url=URL_IMAGE)


@pytest.fixture
def message(chat):
    return Message.objects.create(chat=chat, content="Test message")


@pytest.mark.django_db
class TestChatModel:
    def test_chat_creation(self, chat):
        assert isinstance(chat.id, uuid.UUID)
        assert chat.user.username == "testuser"

    def test_chat_user_relationship(self, chat, user):
        assert chat.user == user
        assert user.chats.first() == chat


@pytest.mark.django_db
class TestExternalImageModel:
    def test_external_image_creation(self, external_image):
        assert isinstance(external_image.id, uuid.UUID)
        assert external_image.external_id == 1
        assert external_image.url == URL_IMAGE
        assert not external_image.was_sent

    def test_external_image_unique_external_id(self, external_image):
        with pytest.raises(IntegrityError):
            ExternalImage.objects.create(external_id=1, url=MOCK_URL_IMAGE_1)

    @patch("chat.models.image.download_image")
    def test_external_image_download(self, mock_download):
        image = ExternalImage.objects.create(
            external_id=2, url=MOCK_URL_IMAGE_2
        )
        mock_download.assert_called_once_with(MOCK_URL_IMAGE_2, image)


@pytest.mark.django_db
class TestMessageModel:
    def test_message_creation(self, message):
        assert isinstance(message.id, uuid.UUID)
        assert message.content == "Test message"
        assert message.image.name is None

    def test_message_with_image(self, chat):
        image = SimpleUploadedFile(
            "test_image.jpg", b"file_content", content_type="image/jpeg"
        )
        message = Message.objects.create(
            chat=chat, content="Test message with image", image=image
        )
        assert message.image.name.startswith("images/")

    def test_message_chat_relationship(self, message, chat):
        assert message.chat == chat
        assert chat.messages.first() == message


@pytest.mark.django_db
class TestModelRelationships:
    def test_user_chat_relationship(self, user, chat):
        assert user.chats.count() == 1
        assert user.chats.first() == chat

    def test_chat_message_relationship(self, chat, message):
        assert chat.messages.count() == 1
        assert chat.messages.first() == message

    def test_cascade_delete(self, user, chat, message):
        user.delete()
        with pytest.raises(Chat.DoesNotExist):
            Chat.objects.get(id=chat.id)
        with pytest.raises(Message.DoesNotExist):
            Message.objects.get(id=message.id)
