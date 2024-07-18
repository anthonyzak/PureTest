import pytest

from chat.providers.factory import ProviderFactory
from chat.providers.sling_academy import SlingAcademyProvider


def test_get_provider_sling_academy():
    provider = ProviderFactory.get_provider("sling_academy")
    assert isinstance(provider, SlingAcademyProvider)


def test_get_provider_unknown():
    with pytest.raises(ValueError):
        ProviderFactory.get_provider("unknown_provider")
