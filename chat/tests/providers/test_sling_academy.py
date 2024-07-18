from unittest.mock import patch

import pytest

from chat.models.image import ExternalImage
from chat.providers.sling_academy import SlingAcademyProvider
from core.settings import API_SLING_ACADEMY_URL

MOCK_SLING_ACADEMY_API_RESPONSE = {
    "success": True,
    "total_photos": 132,
    "message": "Successfully fetched 10 of 132 photos",
    "offset": 0,
    "limit": 10,
    "photos": [
        {
            "url": "https://api.slingacademy.com/public/sample-photos/1.jpeg",
            "user": 28,
            "title": "Defense the travel audience hand",
            "id": 1,
            "description": "Leader structure safe or black late wife"
            "newspaper her pick central forget single likely.",
        },
        {
            "url": "https://api.slingacademy.com/public/sample-photos/2.jpeg",
            "user": 25,
            "title": "Space build policy people model treatment town hard use",
            "id": 2,
            "description": "Much technology how within rather him lay"
            "why part actually system increase feel.",
        },
    ],
}


@pytest.fixture
def sling_provider():
    return SlingAcademyProvider()


@pytest.mark.django_db
@patch("chat.providers.sling_academy.make_request")
def test_fetch_data(mock_request, sling_provider):
    mock_request.return_value = MOCK_SLING_ACADEMY_API_RESPONSE
    result = sling_provider.fetch_data()
    assert "photos" in result
    mock_request.assert_called_once_with(
        API_SLING_ACADEMY_URL, params={"offset": 0, "limit": 10}
    )


@patch("chat.models.image.ExternalImage.objects.filter")
def test_process_data(mock_filter, sling_provider):
    mock_filter.return_value.exists.return_value = False
    result = sling_provider.process_data(MOCK_SLING_ACADEMY_API_RESPONSE)
    assert len(result) == 2
    assert all(key in result[0] for key in ["external_id", "url"])


@pytest.mark.django_db
@patch("chat.models.image.download_image")
def test_save_data(mock_download_image, sling_provider):
    mock_data = [
        {"external_id": 1, "url": "http://test.com/1.jpg"},
        {"external_id": 2, "url": "http://test.com/2.jpg"},
    ]
    sling_provider.save_data(mock_data)
    mock_download_image.return_value = ""
    assert mock_download_image.called
    assert ExternalImage.objects.all().count() == 2
