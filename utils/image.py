import logging
import os
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.db.models import Model

logger = logging.getLogger(__name__)


def download_image(
    url: str, model_instance: Model, field_name: str = "image"
) -> None:
    """
    Downloads an image from a URL and saves it to an
    ImageField of a model instance.

    :param url: The URL of the image to download.
    :param model_instance: The model instance where the image will be saved.
    :param field_name: The name of the ImageField in the model.
        Default is 'image'.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_name = os.path.basename(urlparse(url).path)
        file_content = ContentFile(response.content)
        getattr(model_instance, field_name).save(
            file_name, file_content, save=False
        )
    except requests.RequestException as e:
        logger.error(f"Failed to download image from {url}. Error: {e}")
