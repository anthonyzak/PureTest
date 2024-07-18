from abc import ABC
from typing import Any, Dict, List

import pytest

from chat.providers.base import BaseProvider


class TestProvider(BaseProvider):
    def fetch_data(self) -> Dict[str, Any]:
        return {"data": [1, 2, 3, 4, 5]}

    def process_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"value": x * 2} for x in data["data"]]

    def save_data(self, processed_data: List[Dict[str, Any]]) -> None:
        self.saved_data = processed_data


def test_base_provider_is_abstract():
    assert issubclass(BaseProvider, ABC)
    with pytest.raises(TypeError):
        BaseProvider()


def test_concrete_provider_instantiation():
    provider = TestProvider()
    assert isinstance(provider, BaseProvider)


def test_fetch_data():
    provider = TestProvider()
    data = provider.fetch_data()
    assert isinstance(data, dict)
    assert "data" in data
    assert data["data"] == [1, 2, 3, 4, 5]


def test_process_data():
    provider = TestProvider()
    raw_data = {"data": [1, 2, 3, 4, 5]}
    processed_data = provider.process_data(raw_data)
    assert isinstance(processed_data, list)
    assert all(isinstance(item, dict) for item in processed_data)
    assert processed_data == [
        {"value": 2},
        {"value": 4},
        {"value": 6},
        {"value": 8},
        {"value": 10},
    ]


def test_save_data():
    provider = TestProvider()
    processed_data = [{"value": 2}, {"value": 4}, {"value": 6}]
    provider.save_data(processed_data)
    assert hasattr(provider, "saved_data")
    assert provider.saved_data == processed_data


def test_full_process():
    provider = TestProvider()
    raw_data = provider.fetch_data()
    processed_data = provider.process_data(raw_data)
    provider.save_data(processed_data)
    assert provider.saved_data == [
        {"value": 2},
        {"value": 4},
        {"value": 6},
        {"value": 8},
        {"value": 10},
    ]
