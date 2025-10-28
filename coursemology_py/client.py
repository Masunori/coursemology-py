import os
from urllib.parse import unquote, urlparse

import requests

from coursemology_py.api.course import CourseAPI
from coursemology_py.api.courses import CoursesAPI
from coursemology_py.api.jobs import JobsAPI
from coursemology_py.auth import CoursemologyAuthenticator, CoursemologySession
from coursemology_py.exceptions import CoursemologyAPIError


class CoursemologyClient:
    """
    The main client for interacting with the Coursemology API.

    This class handles authentication and provides access to various API handlers.
    """

    def __init__(self, host: str = "https://coursemology.org"):
        """
        Initializes the client.

        Args:
            host: The base URL of the Coursemology instance (e.g., "https://coursemology.org").
        """
        self.host = host
        self.base_url = f"{host}"
        self._authenticator = CoursemologyAuthenticator(redirect_uri=host)
        self._session: CoursemologySession | None = None

        # Private attributes to cache the handler instances upon first access
        self._jobs: JobsAPI | None = None
        self._courses: CoursesAPI | None = None

    def login(self, username: str, password: str) -> None:
        """
        Authenticates with the Coursemology instance and prepares the client
        for making API calls. This method must be called before accessing any APIs.

        Args:
            username: The user's username or email.
            password: The user's password.
        """
        print("Logging in...")
        self._session = self._authenticator.get_api_session(username, password)
        print("Login successful.")

    @property
    def jobs(self) -> JobsAPI:
        """Provides access to the Jobs API handler for checking background job statuses."""
        if not self._session:
            raise CoursemologyAPIError("You must call .login() before accessing APIs.")
        if self._jobs is None:
            self._jobs = JobsAPI(self._session, self.base_url)
        return self._jobs

    @property
    def courses(self) -> CoursesAPI:
        """Provides access to the top-level Courses API handler for listing and creating courses."""
        if not self._session:
            raise CoursemologyAPIError("You must call .login() before accessing APIs.")
        if self._courses is None:
            self._courses = CoursesAPI(self._session, self.base_url)
        return self._courses

    def course(self, course_id: int) -> CourseAPI:
        """
        Returns an API handler for a specific course.

        Args:
            course_id: The ID of the course to interact with.

        Returns:
            An instance of CourseAPI configured for the specified course.
        """
        if not self._session:
            raise CoursemologyAPIError("You must call .login() before accessing APIs.")
        return CourseAPI(self._session, self.base_url, course_id)

    def download_file(self, url: str, local_path: str | None = None) -> str:
        """
        Downloads a file from a given URL using the client's authenticated session.
        """
        if not self._session:
            raise CoursemologyAPIError("You must be logged in to download files.")

        print(f"Downloading file from: {url}")
        try:
            response = self._session.get(url, stream=True)
            response.raise_for_status()

            final_path = local_path
            if not final_path:
                if "content-disposition" in response.headers:
                    disposition = response.headers["content-disposition"]
                    try:
                        # Use the correct unquote function from urllib.parse
                        fn = unquote(disposition.split("filename=")[1].strip('"'))
                        if fn:
                            final_path = fn
                    except IndexError:
                        pass

                if not final_path:
                    final_path = os.path.basename(urlparse(url).path)

                if not final_path:
                    final_path = "downloaded_file"

            with open(final_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Successfully downloaded and saved file as '{final_path}'")
            return final_path

        except requests.exceptions.RequestException as e:
            raise OSError(f"Failed to download the file: {e}") from e
