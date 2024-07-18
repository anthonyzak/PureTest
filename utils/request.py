from typing import Any, Dict

import requests
from celery.utils.log import get_task_logger
from requests.exceptions import HTTPError, RequestException

from utils.exceptions import (
    ExternalAPIUnavailableError,
    InternalError,
    UnexpectedResponseError,
)

logger = get_task_logger(__name__)


def make_request(url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Makes a GET request to the specified URL with the given parameters.

    :param url: The URL to which the request will be made.
    :param params: The parameters for the request. Defaults to None.
    :return: The JSON response from the request.
    :raises ExternalAPIUnavailableError: If the external API is not available.
    :raises UnexpectedResponseError: If the server response is unexpected.
    :raises InternalError: For any other internal error.
    """
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as exc:
        if isinstance(exc, HTTPError):
            logger.error(f"Error in the server response: {exc}")
            raise UnexpectedResponseError(
                "The server response is not as expected"
            )
        else:
            logger.error(f"Error when making the request: {exc}")
            raise ExternalAPIUnavailableError(
                "The external API is not available at this time"
            )
    except Exception as exc:
        logger.error(f"Unexpected error: {exc}")
        raise InternalError(
            "An internal error occurred while processing the request"
        )
