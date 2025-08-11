"""Tests for HTTP error mapping and exception handling."""

from unittest.mock import MagicMock

from poke_api._exceptions import (
    APIStatusError,
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PokeAPIError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    UnauthorizedError,
    UnprocessableEntityError,
    map_http_error,
)


class TestExceptionMapping:
    """Test suite for HTTP status code to exception mapping."""

    def test_400_bad_request(self):
        """Test that 400 status maps to BadRequestError."""
        error = map_http_error(400, "Invalid request format")
        assert isinstance(error, BadRequestError)
        assert error.status_code == 400
        assert str(error) == "Invalid request format"

    def test_401_unauthorized(self):
        """Test that 401 status maps to UnauthorizedError."""
        error = map_http_error(401, "Authentication required")
        assert isinstance(error, UnauthorizedError)
        assert error.status_code == 401
        assert str(error) == "Authentication required"

    def test_403_forbidden(self):
        """Test that 403 status maps to ForbiddenError."""
        error = map_http_error(403, "Access denied")
        assert isinstance(error, ForbiddenError)
        assert error.status_code == 403
        assert str(error) == "Access denied"

    def test_404_not_found(self):
        """Test that 404 status maps to NotFoundError."""
        error = map_http_error(404, "Resource not found")
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404
        assert str(error) == "Resource not found"

    def test_409_conflict(self):
        """Test that 409 status maps to ConflictError."""
        error = map_http_error(409, "Resource conflict")
        assert isinstance(error, ConflictError)
        assert error.status_code == 409
        assert str(error) == "Resource conflict"

    def test_422_unprocessable_entity(self):
        """Test that 422 status maps to UnprocessableEntityError."""
        error = map_http_error(422, "Validation failed")
        assert isinstance(error, UnprocessableEntityError)
        assert error.status_code == 422
        assert str(error) == "Validation failed"

    def test_429_rate_limit(self):
        """Test that 429 status maps to RateLimitError."""
        error = map_http_error(429, "Too many requests")
        assert isinstance(error, RateLimitError)
        assert error.status_code == 429
        # Rate limit errors should use a specific message
        assert str(error) == "Rate limited"

    def test_500_server_error(self):
        """Test that 500 status maps to ServerError."""
        error = map_http_error(500, "Internal server error")
        assert isinstance(error, ServerError)
        assert error.status_code == 500
        assert str(error) == "Internal server error"

    def test_501_server_error(self):
        """Test that 501 status maps to ServerError."""
        error = map_http_error(501, "Not implemented")
        assert isinstance(error, ServerError)
        assert error.status_code == 501
        assert str(error) == "Not implemented"

    def test_502_service_unavailable(self):
        """Test that 502 status maps to ServiceUnavailableError."""
        error = map_http_error(502, "Bad gateway")
        assert isinstance(error, ServiceUnavailableError)
        assert isinstance(error, ServerError)  # Should also be a ServerError
        assert error.status_code == 502
        assert str(error) == "Bad gateway"

    def test_503_service_unavailable(self):
        """Test that 503 status maps to ServiceUnavailableError."""
        error = map_http_error(503, "Service unavailable")
        assert isinstance(error, ServiceUnavailableError)
        assert isinstance(error, ServerError)  # Should also be a ServerError
        assert error.status_code == 503
        assert str(error) == "Service unavailable"

    def test_504_service_unavailable(self):
        """Test that 504 status maps to ServiceUnavailableError."""
        error = map_http_error(504, "Gateway timeout")
        assert isinstance(error, ServiceUnavailableError)
        assert isinstance(error, ServerError)  # Should also be a ServerError
        assert error.status_code == 504
        assert str(error) == "Gateway timeout"

    def test_unknown_4xx_status(self):
        """Test that unknown 4xx status maps to APIStatusError."""
        error = map_http_error(418, "I'm a teapot")
        assert isinstance(error, APIStatusError)
        assert not isinstance(error, BadRequestError)  # Should not be a specific error
        assert error.status_code == 418
        assert str(error) == "I'm a teapot"

    def test_unknown_5xx_status(self):
        """Test that unknown 5xx status maps to ServerError."""
        error = map_http_error(599, "Custom server error")
        assert isinstance(error, ServerError)
        assert not isinstance(error, ServiceUnavailableError)
        assert error.status_code == 599
        assert str(error) == "Custom server error"

    def test_no_body(self):
        """Test mapping without body content."""
        error = map_http_error(404)
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404
        assert str(error) == "HTTP 404"  # Should use default message

    def test_none_body(self):
        """Test mapping with None body."""
        error = map_http_error(500, None)
        assert isinstance(error, ServerError)
        assert error.status_code == 500
        assert str(error) == "HTTP 500"  # Should use default message

    def test_complex_body(self):
        """Test mapping with complex body object."""
        complex_body = {"error": "validation_failed", "details": ["field1", "field2"]}
        error = map_http_error(422, complex_body)
        assert isinstance(error, UnprocessableEntityError)
        assert error.status_code == 422
        assert str(complex_body) in str(error)

    def test_inheritance_hierarchy(self):
        """Test that all exception classes have correct inheritance."""
        # Test specific error inheritance
        assert issubclass(BadRequestError, APIStatusError)
        assert issubclass(UnauthorizedError, APIStatusError)
        assert issubclass(ForbiddenError, APIStatusError)
        assert issubclass(NotFoundError, APIStatusError)
        assert issubclass(ConflictError, APIStatusError)
        assert issubclass(UnprocessableEntityError, APIStatusError)
        assert issubclass(RateLimitError, APIStatusError)
        assert issubclass(ServerError, APIStatusError)
        assert issubclass(ServiceUnavailableError, ServerError)

        # Test base inheritance
        assert issubclass(APIStatusError, PokeAPIError)
        assert issubclass(PokeAPIError, Exception)


class TestExceptionProperties:
    """Test exception class properties and methods."""

    def test_api_status_error_with_status_code(self):
        """Test APIStatusError stores status code properly."""
        error = APIStatusError(404, "Not found")
        assert error.status_code == 404
        assert str(error) == "Not found"

    def test_api_status_error_default_message(self):
        """Test APIStatusError uses default message when none provided."""
        error = APIStatusError(500)
        assert error.status_code == 500
        assert str(error) == "HTTP 500"

    def test_specific_errors_preserve_status_code(self):
        """Test that specific error classes preserve status codes."""
        errors = [
            (BadRequestError(400, "Bad request"), 400),
            (UnauthorizedError(401, "Unauthorized"), 401),
            (ForbiddenError(403, "Forbidden"), 403),
            (NotFoundError(404, "Not found"), 404),
            (ConflictError(409, "Conflict"), 409),
            (UnprocessableEntityError(422, "Invalid"), 422),
            (RateLimitError(429, "Rate limited"), 429),
            (ServerError(500, "Server error"), 500),
            (ServiceUnavailableError(503, "Unavailable"), 503),
        ]

        for error, expected_code in errors:
            assert error.status_code == expected_code
            assert hasattr(error, "status_code")


class TestSafeGetResponseBody:
    """Test the _safe_get_response_body helper function."""

    def test_json_response_body(self):
        """Test extracting JSON response body."""
        from poke_api._client import _safe_get_response_body

        # Mock response with JSON
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "not found", "code": 404}
        mock_response.text = '{"error": "not found", "code": 404}'

        body = _safe_get_response_body(mock_response)
        assert "not found" in body
        assert "404" in body

    def test_text_response_body_fallback(self):
        """Test fallback to text when JSON parsing fails."""
        from poke_api._client import _safe_get_response_body

        # Mock response that raises exception on json()
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Plain text error message"

        body = _safe_get_response_body(mock_response)
        assert body == "Plain text error message"

    def test_long_text_response_truncation(self):
        """Test that long text responses are truncated."""
        from poke_api._client import _safe_get_response_body

        # Mock response with very long text
        long_text = "x" * 300  # Longer than 200 chars
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = long_text

        body = _safe_get_response_body(mock_response)
        assert len(body) == 200
        assert body == "x" * 200
