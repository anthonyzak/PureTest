class ExternalAPIUnavailableError(Exception):
    """Exception raised when the API is unavailable"""


class UnexpectedResponseError(Exception):
    """Exception raised when the API gives
    an unexpected response."""


class InternalError(Exception):
    """Exception raised when the API gives
    an internal error."""
