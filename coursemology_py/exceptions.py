from typing import Any

from requests import Response


class CoursemologyAPIError(Exception):
    """Base exception for all errors related to the Coursemology API client."""

    pass


class APIError(CoursemologyAPIError):
    """
    Represents an error returned by the Coursemology API (e.g., HTTP 4xx or 5xx).
    """

    def __init__(
        self,
        message: str,
        *,
        response: Response,
        api_errors: Any | None = None,
    ):
        super().__init__(message)
        self.response = response
        self.request = response.request
        self.status_code = response.status_code
        self.api_errors = api_errors

    def __str__(self) -> str:
        base_message = f"HTTP {self.status_code} on {self.request.method} {self.request.url}"

        if self.api_errors:
            return f"{base_message}: {self.api_errors}"

        # Truncate long HTML responses for readability
        response_text = self.response.text
        if "</html>" in response_text.lower():
            response_text = f"{response_text[:200]}..."

        return f"{base_message}: {response_text}"


# --- Specific HTTP Error Categories ---


class ClientError(APIError):
    """Represents a 4xx client error (e.g., 404 Not Found, 403 Forbidden)."""

    pass


class ServerError(APIError):
    """Represents a 5xx server error (e.g., 500 Internal Server Error, 502 Bad Gateway)."""

    pass


class NonJSONResponseError(ServerError):
    """
    A specific type of server error where the response was expected to be JSON
    but was not (e.g., an HTML error page).
    """

    pass
