from typing import IO

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.user_invitations import (
    CourseRegistrationKeyResponse,
    InvitationsFormPayload,
    InviteResponse,
    ResendAllResponse,
    UserInvitation,
    UserInvitationsIndexResponse,
)
from coursemology_py.utils import build_form_data


class UserInvitationsAPI(BaseCourseAPI):
    """
    API handler for inviting users and managing invitations.
    Mirrors `coursemology2/client/app/api/course/UserInvitations.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        # The methods in this API construct their own paths relative to the course URL.
        return super()._url_prefix

    def index(self) -> UserInvitationsIndexResponse:
        """Fetches data from the user invitations index page."""
        return self._get("user_invitations", response_model=UserInvitationsIndexResponse)

    def invite_from_file(self, file: IO[bytes]) -> InviteResponse:
        """
        Invites users from a CSV file.

        Args:
            file: A file-like object containing the CSV data.
        """
        files = {"course[invitations_file]": file}
        return self._post("users/invite", files=files, response_model=InviteResponse)

    def invite_from_form(self, payload: InvitationsFormPayload) -> InviteResponse:
        """
        Invites one or more users using a structured payload object.

        Args:
            payload: An InvitationsFormPayload object containing a list of users to invite.
        """
        form_data = build_form_data(payload, "course")
        return self._post("users/invite", data=form_data, response_model=InviteResponse)

    def get_course_registration_key(self) -> CourseRegistrationKeyResponse:
        """Fetches the course registration key."""
        return self._get("users/invite", response_model=CourseRegistrationKeyResponse)

    def get_permissions_and_shared_data(self) -> UserInvitationsIndexResponse:
        """Fetches permissions and shared course data without the invitation list."""
        return self._get(
            "user_invitations",
            params={"without_invitations": "true"},
            response_model=UserInvitationsIndexResponse,
        )

    def toggle_course_registration_key(self, enable: bool) -> CourseRegistrationKeyResponse:
        """Enables or disables the course registration code."""
        payload = {"course": {"registration_key": "checked"}} if enable else {}
        return self._post(
            "users/toggle_registration",
            json=payload,
            response_model=CourseRegistrationKeyResponse,
        )

    def resend_all_invitations(self) -> ResendAllResponse:
        """Resends all pending invitation emails."""
        return self._post("users/resend_invitations", response_model=ResendAllResponse)

    def resend_invitation_email(self, invitation_id: int) -> UserInvitation:
        """Resends a single invitation email."""
        return self._post(
            f"user_invitations/{invitation_id}/resend_invitation",
            response_model=UserInvitation,
        )

    def delete(self, invitation_id: int) -> None:
        """Deletes a pending invitation."""
        self._delete(f"user_invitations/{invitation_id}")
