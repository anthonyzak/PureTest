import uuid

from django.db import models

from core.models import BaseModel
from utils.image import download_image


class ExternalImage(BaseModel):
    """External image model"""

    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False,
    )
    external_id = models.IntegerField(unique=True)
    url = models.URLField()
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    was_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.url and not self.image:
            download_image(self.url, self)
        super().save(*args, **kwargs)
