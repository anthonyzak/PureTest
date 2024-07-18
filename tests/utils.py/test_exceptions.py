import pytest

from utils.exceptions import (
    ExternalAPIUnavailableError,
    InternalError,
    UnexpectedResponseError,
)


@pytest.mark.parametrize(
    "exception_class",
    [ExternalAPIUnavailableError, UnexpectedResponseError, InternalError],
)
def test_custom_exceptions(exception_class):
    with pytest.raises(exception_class):
        raise exception_class("Test error message")


def test_exception_inheritance():
    assert issubclass(ExternalAPIUnavailableError, Exception)
    assert issubclass(UnexpectedResponseError, Exception)
    assert issubclass(InternalError, Exception)
