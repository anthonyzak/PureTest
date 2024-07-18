from unittest.mock import MagicMock, patch

import pytest

from chat.models import ExternalImage
from utils.image import download_image


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.content = b"fake image content"
    return mock


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url,field_name",
    [
        ("http://test.com/photo_test.jpg", "image"),
    ],
)
def test_download_image_success(url, field_name, mock_response):
    with patch("requests.get", return_value=mock_response):
        model_instance = ExternalImage()
        download_image(url, model_instance, field_name)
        assert getattr(model_instance, field_name).name.startswith("images/")


@pytest.mark.django_db
@patch("logging.Logger.error")
@patch("utils.image.requests.get")
def test_download_image_failure(mock_request, mock_logger):
    mock_request.side_effect = Exception("Network error")
    with pytest.raises(Exception):
        model_instance = ExternalImage()
        download_image("http://example.com/image.jpg", model_instance)
        assert mock_logger.assert_called_once()
        assert not model_instance.image
