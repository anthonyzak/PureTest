from unittest.mock import MagicMock, patch

import pytest

from chat.tasks import fetch_photos_from_api


@pytest.fixture
def mock_provider():
    provider = MagicMock()
    provider.fetch_data.return_value = {
        "photos": [{"id": 1, "url": "http://test.com/1.jpg"}]
    }
    provider.process_data.return_value = [
        {"external_id": 1, "url": "http://test.com/1.jpg"}
    ]
    return provider


@patch("chat.providers.factory.ProviderFactory.get_provider")
def test_fetch_photos_from_api(mock_get_provider, mock_provider):
    mock_get_provider.return_value = mock_provider
    fetch_photos_from_api("sling_academy")
    mock_provider.fetch_data.assert_called_once()
    mock_provider.process_data.assert_called_once()
    mock_provider.save_data.assert_called_once()


@patch("chat.tasks.ProviderFactory.get_provider")
def test_fetch_photos_from_api_exception(mock_get_provider):
    mock_get_provider.side_effect = Exception("Error test")
    with pytest.raises(Exception) as excinfo:
        fetch_photos_from_api("sling_academy")
        assert "Error" in excinfo.value.message
