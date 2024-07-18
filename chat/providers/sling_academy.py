from typing import Any, Dict, List

from chat.models.image import ExternalImage
from chat.providers import BaseProvider
from core.settings import API_SLING_ACADEMY_URL
from utils.request import make_request


class SlingAcademyProvider(BaseProvider):
    def fetch_data(self) -> Dict[str, Any]:
        offset = ExternalImage.objects.count()
        return make_request(
            API_SLING_ACADEMY_URL, params={"offset": offset, "limit": 10}
        )

    def process_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        images = data.get("photos", [])
        new_images = []
        for image in images:
            photo_id = image["id"]
            if not ExternalImage.objects.filter(external_id=photo_id).exists():
                new_images.append(
                    {"external_id": photo_id, "url": image["url"]}
                )
        return new_images

    def save_data(self, processed_data: List[Dict[str, Any]]) -> None:
        for image_data in processed_data:
            image = ExternalImage(**image_data)
            image.save()
