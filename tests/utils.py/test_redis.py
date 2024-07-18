import json
from unittest.mock import MagicMock, patch

import pytest

from utils.redis import cache_decorator


@pytest.fixture
def mock_redis():
    with patch("utils.redis.redis_client") as mock:
        yield mock


@pytest.fixture
def decorated_function():
    @cache_decorator()
    def test_func(self, request, image_data, cache_key, *args, **kwargs):
        return image_data, cache_key

    return test_func


def test_cache_decorator_with_cache_key(mock_redis, decorated_function):
    mock_self = MagicMock()
    mock_request = MagicMock()
    mock_redis.lrange.return_value = [json.dumps({"test": "data"})]

    result = decorated_function(mock_self, mock_request, cache_key="test_key")

    mock_redis.lrange.assert_called_once_with("test_key", 0, -1)
    mock_redis.lpop.assert_called_once_with("test_key")
    assert result == ({"test": "data"}, "test_key")


def test_cache_decorator_without_cache_key(mock_redis, decorated_function):
    mock_self = MagicMock()
    mock_request = MagicMock()

    result = decorated_function(mock_self, mock_request)

    mock_redis.lrange.assert_not_called()
    mock_redis.lpop.assert_not_called()
    assert result == (None, None)


def test_cache_decorator_empty_cache(mock_redis, decorated_function):
    mock_self = MagicMock()
    mock_request = MagicMock()
    mock_redis.lrange.return_value = []

    result = decorated_function(mock_self, mock_request, cache_key="test_key")

    mock_redis.lrange.assert_called_once_with("test_key", 0, -1)
    mock_redis.lpop.assert_not_called()
    assert result == (None, "test_key")
