from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.exceptions import RequestException

from utils.exceptions import (
    ExternalAPIUnavailableError,
    InternalError,
    UnexpectedResponseError,
)
from utils.request import make_request


@pytest.fixture
def mock_requests():
    with patch("utils.request.requests.get") as mock:
        yield mock


def test_make_request_success(mock_requests):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_requests.return_value = mock_response

    result = make_request("http://test.com", {"param": "value"})

    mock_requests.assert_called_once_with(
        "http://test.com", params={"param": "value"}
    )
    assert result == {"data": "test"}


def test_make_request_external_api_unavailable(mock_requests):
    mock_requests.side_effect = RequestException()

    with pytest.raises(ExternalAPIUnavailableError):
        make_request("http://test.com")


def test_make_request_unexpected_response(mock_requests):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError()
    mock_requests.return_value = mock_response

    with pytest.raises(UnexpectedResponseError):
        make_request("http://test.com")


def test_make_request_api_unavailable(mock_requests):
    mock_requests.side_effect = requests.ConnectionError()

    with pytest.raises(ExternalAPIUnavailableError):
        make_request("http://test.com")


def test_make_request_internal_error(mock_requests):
    mock_requests.side_effect = Exception()

    with pytest.raises(InternalError):
        make_request("http://test.com")


@pytest.mark.parametrize(
    "url,params",
    [
        ("http://test.com", None),
        ("http://test.com", {"param": "value"}),
        ("https://api.example.com", {"id": 123, "type": "user"}),
    ],
)
def test_make_request_different_params(mock_requests, url, params):
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": "test"}
    mock_requests.return_value = mock_response

    result = make_request(url, params)

    mock_requests.assert_called_once_with(url, params=params)
    assert result == {"data": "test"}
