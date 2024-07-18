import uuid

from django.db import models

from chat.models import Chat
from core.models import BaseModel


class Message(BaseModel):
    """Message model"""

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )
    chat = models.ForeignKey(
        Chat, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    image = models.ImageField(upload_to="images/", null=True, blank=True)
