from typing import IO
from urllib.parse import urlparse

from coursemology_py.api.base import BaseAPI
from coursemology_py.models.courses import (
    CourseCreatePayload,
    CourseCreateResponse,
    CourseFetchResponse,
    CourseLayoutData,
    CoursesIndexResponse,
)


class CoursesAPI(BaseAPI):
    """
    API handler for listing, fetching, and creating courses.
    Mirrors `coursemology2/client/app/api/course/Courses.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        return "/courses"

    def _get_relative_path(self, full_url: str) -> str:
        """Strips the host prefix to get a relative path."""
        api_prefix = urlparse(self._base_url).path
        full_path = urlparse(full_url).path
        if full_path.startswith(api_prefix):
            return full_path[len(api_prefix) :]
        return full_path

    def index(self) -> CoursesIndexResponse:
        """Fetches a list of all courses visible to the user."""
        return self._get("", response_model=CoursesIndexResponse)

    def fetch(self, course_id: int) -> CourseFetchResponse:
        """Fetches detailed information for a single course."""
        return self._get(f"{course_id}", response_model=CourseFetchResponse)

    def fetch_layout(self, course_id: int) -> CourseLayoutData:
        """Fetches the sidebar layout for a course."""
        return self._get(f"{course_id}/sidebar", response_model=CourseLayoutData)

    def create(self, payload: CourseCreatePayload, logo: IO[bytes] | None = None) -> CourseCreateResponse:
        """
        Creates a new course.

        Args:
            payload: A Pydantic model containing the course's data.
            logo: An optional file-like object for the course logo.
        """
        data = {f"course[{key}]": value for key, value in payload.model_dump(by_alias=True, exclude_none=True).items()}
        files = {}
        if logo:
            files["course[logo]"] = logo

        return self._post("", data=data, files=files, response_model=CourseCreateResponse)

    def remove_todo(self, ignore_link: str) -> None:
        """Removes a 'todo' item by posting to its ignore link."""
        relative_path = self._get_relative_path(ignore_link)
        self._post(relative_path)

    def send_new_registration_code(self, registration_link: str, form_data: dict[str, str]) -> None:
        """Submits a new registration code."""
        relative_path = self._get_relative_path(registration_link)
        self._post(relative_path, data=form_data)

    def submit_enrol_request(self, link: str) -> None:
        """Submits an enrollment request for a course."""
        relative_path = self._get_relative_path(link)
        self._post(relative_path)

    def cancel_enrol_request(self, link: str) -> None:
        """Cancels a pending enrollment request."""
        relative_path = self._get_relative_path(link)
        self._delete(relative_path)
