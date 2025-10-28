from typing import Any, Literal, TypeVar

from pydantic import TypeAdapter
from requests import Response
from requests.exceptions import HTTPError, JSONDecodeError

from coursemology_py.auth import CoursemologySession
from coursemology_py.exceptions import (
    APIError,
    ClientError,
    NonJSONResponseError,
    ServerError,
)

T = TypeVar("T")
HttpMethod = Literal["GET", "POST", "PATCH", "PUT", "DELETE"]


class BaseAPI:
    """
    The fundamental base class for all API endpoint handlers.

    It holds the authenticated session and provides helper methods for making
    HTTP requests that raise specific, informative exceptions on failure and
    can automatically parse successful responses into Pydantic models.
    """

    def __init__(self, session: CoursemologySession, base_url: str):
        self._session = session
        self._base_url = base_url

    @property
    def _url_prefix(self) -> str:
        """
        The URL prefix for all endpoints in this API. Subclasses override this.
        """
        return ""

    def _get_csrf_token(self) -> str | None:
        """Extracts the CSRF token from the session object."""
        return self._session._csrf_token  # type: ignore

    def _handle_response(self, response: Response, response_model: type[T] | None = None) -> T | Any:
        """
        A centralized helper to process the response, handle errors, and parse data.
        """
        try:
            response.raise_for_status()
        except HTTPError as e:
            api_errors = None
            try:
                error_json = response.json()
                api_errors = error_json.get("errors") or error_json.get("error")
            except (JSONDecodeError, AttributeError):
                pass

            status_code = response.status_code
            message = f"API request failed with status {status_code}."

            if api_errors:
                message = f"{message}: {api_errors}"

            if 400 <= status_code < 500:
                raise ClientError(message, response=response, api_errors=api_errors) from e
            elif 500 <= status_code < 600:
                raise ServerError(message, response=response, api_errors=api_errors) from e
            else:
                raise APIError(message, response=response, api_errors=api_errors) from e

        try:
            if not response.content:
                return None
            json_data = response.json()
            # print("RESPONSE:", json_data)
            if response_model:
                return TypeAdapter(response_model).validate_python(json_data)
            return json_data
        except JSONDecodeError as e:
            raise NonJSONResponseError(
                "The API returned a successful status code but an invalid JSON body.",
                response=response,
            ) from e

    def _request(
        self,
        method: HttpMethod,
        path: str,
        *,
        response_model: type[T] | None = None,
        **kwargs: Any,
    ) -> T | Any:
        """
        A single, centralized method for making all API requests.

        This method handles URL construction, CSRF token injection, making the
        request, and processing the response.
        """
        # 1. Construct the full URL
        if path.startswith("/"):
            # If path starts with '/', treat it as an absolute path from the host.
            full_path = path
        else:
            # Otherwise, join it with the prefix.
            prefix = self._url_prefix
            full_path = "/".join(part for part in [prefix, path] if part)

        # Use rstrip and lstrip to prevent double slashes and ensure correctness
        url = f"{self._base_url.rstrip('/')}/{full_path.lstrip('/')}"

        # 2. Prepare parameters, ensuring format=json is set
        params = kwargs.get("params")
        if params is None:
            params = {}
        if "format" not in params:
            params["format"] = "json"
        kwargs["params"] = params

        # 3. Add CSRF token for state-changing methods
        if method in ["POST", "PATCH", "PUT", "DELETE"]:
            csrf_token = self._get_csrf_token()
            if csrf_token:
                headers = kwargs.setdefault("headers", {})
                headers["X-CSRF-Token"] = csrf_token

        # 4. Special handling to convert boolean values to "true"/"false" strings if using form data
        if "data" in kwargs and isinstance(kwargs["data"], dict):
            for k, v in kwargs["data"].items():
                kwargs["data"][k] = str(v).lower() if isinstance(v, bool) else v

        # print(f"REQUEST: {method} {url} with {kwargs}")

        # 5. Make the request dynamically and handle the response
        request_method = getattr(self._session, method.lower())
        response = request_method(url, **kwargs)
        return self._handle_response(response, response_model)
    
    def _get(self, path: str, *, response_model: type[T] | None = None, **kwargs: Any) -> T | Any:
        """Performs a GET request."""
        return self._request("GET", path, response_model=response_model, **kwargs)

    def _post(self, path: str, *, response_model: type[T] | None = None, **kwargs: Any) -> T | Any:
        """Performs a POST request."""
        return self._request("POST", path, response_model=response_model, **kwargs)

    def _patch(self, path: str, *, response_model: type[T] | None = None, **kwargs: Any) -> T | Any:
        """Performs a PATCH request."""
        return self._request("PATCH", path, response_model=response_model, **kwargs)

    def _put(self, path: str, *, response_model: type[T] | None = None, **kwargs: Any) -> T | Any:
        """Performs a PUT request."""
        return self._request("PUT", path, response_model=response_model, **kwargs)

    def _delete(self, path: str, *, response_model: type[T] | None = None, **kwargs: Any) -> T | Any:
        """Performs a DELETE request."""
        return self._request("DELETE", path, response_model=response_model, **kwargs)


class BaseCourseAPI(BaseAPI):
    """
    A specialized base class for APIs that operate within the context of a
    specific course. It automatically constructs the URL prefix.
    """

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int):
        super().__init__(session, base_url)
        self._course_id = course_id

    @property
    def _url_prefix(self) -> str:
        """The base path for all course-level API calls."""
        return f"courses/{self._course_id}"
