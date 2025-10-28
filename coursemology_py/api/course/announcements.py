from typing import IO

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.announcements import (
    Announcement,
    AnnouncementPayload,
    AnnouncementsIndexResponse,
)


class AnnouncementsAPI(BaseCourseAPI):
    """
    API handler for course announcements.
    Mirrors `coursemology2/client/app/api/course/Announcements.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/announcements"

    def index(self) -> AnnouncementsIndexResponse:
        """Fetches all announcements for the course."""
        return self._get("", response_model=AnnouncementsIndexResponse)

    def create(self, payload: AnnouncementPayload, attachment: IO[bytes] | None = None) -> Announcement:
        """
        Creates a new announcement.
        """
        # The API expects form data, nested under 'announcement'.
        data = {
            f"announcement[{key}]": value for key, value in payload.model_dump(by_alias=True, exclude_none=True).items()
        }

        files = {}
        if attachment:
            files["announcement[attachment]"] = attachment

        return self._post("", data=data, files=files, response_model=Announcement)

    def update(
        self,
        announcement_id: int,
        payload: AnnouncementPayload,
        attachment: IO[bytes] | None = None,
    ) -> Announcement:
        """
        Updates an existing announcement.
        """
        data = {
            f"announcement[{key}]": value for key, value in payload.model_dump(by_alias=True, exclude_none=True).items()
        }

        files = {}
        if attachment:
            files["announcement[attachment]"] = attachment

        return self._patch(f"{announcement_id}", data=data, files=files, response_model=Announcement)

    def delete(self, announcement_id: int) -> None:
        """Deletes an announcement."""
        self._delete(f"{announcement_id}")
