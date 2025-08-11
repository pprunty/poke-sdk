# src/poke_api/_exceptions.py

from typing import Any


class PokeAPIError(Exception):
    """Base exception for all SDK errors."""


class APIConnectionError(PokeAPIError):
    """Network/transport problem talking to PokeAPI."""


class APITimeoutError(PokeAPIError):
    """Request timed out."""


class APIStatusError(PokeAPIError):
    """Non-2xx HTTP status."""

    def __init__(self, status_code: int, message: str | None = None):
        self.status_code = status_code
        super().__init__(message or f"HTTP {status_code}")


class BadRequestError(APIStatusError):
    """400 Bad Request."""


class UnauthorizedError(APIStatusError):
    """401 Unauthorized."""


class ForbiddenError(APIStatusError):
    """403 Forbidden."""


class NotFoundError(APIStatusError):
    """404 Not Found."""


class ConflictError(APIStatusError):
    """409 Conflict."""


class UnprocessableEntityError(APIStatusError):
    """422 Unprocessable Entity."""


class RateLimitError(APIStatusError):
    """429 Too Many Requests."""


class ServerError(APIStatusError):
    """5xx Server Error."""


class ServiceUnavailableError(ServerError):
    """502/503/504 Service Unavailable."""


def map_http_error(status_code: int, body: Any = None) -> APIStatusError:
    """Map HTTP status codes to appropriate exception classes.

    Args:
        status_code: HTTP status code
        body: Response body (optional)

    Returns:
        Appropriate APIStatusError subclass instance
    """
    message = str(body) if body else None

    # Client errors (4xx)
    if status_code == 400:
        return BadRequestError(status_code, message)
    elif status_code == 401:
        return UnauthorizedError(status_code, message)
    elif status_code == 403:
        return ForbiddenError(status_code, message)
    elif status_code == 404:
        return NotFoundError(status_code, message)
    elif status_code == 409:
        return ConflictError(status_code, message)
    elif status_code == 422:
        return UnprocessableEntityError(status_code, message)
    elif status_code == 429:
        return RateLimitError(status_code, "Rate limited")

    # Server errors (5xx)
    elif 500 <= status_code < 600:
        if status_code in (502, 503, 504):
            return ServiceUnavailableError(status_code, message)
        else:
            return ServerError(status_code, message)

    # Fallback for other status codes
    else:
        return APIStatusError(status_code, message)
