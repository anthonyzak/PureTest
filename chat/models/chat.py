import uuid

from django.db import models

from account.models import CustomUser
from core.models import BaseModel


class Chat(BaseModel):
    """Chat model"""

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="chats"
    )
