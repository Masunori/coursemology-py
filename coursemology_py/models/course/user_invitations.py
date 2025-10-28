import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Import shared models from the users module
from coursemology_py.models.course.users import (
    CourseUser,
    CourseUserRoles,
    ManageCourseUsersPermissions,
    ManageCourseUsersSharedData,
    TimelineAlgorithm,
)


class UserInvitation(BaseModel):
    """
    Represents a single user invitation with all its details.
    Corresponds to `InvitationListData` in TypeScript.
    """

    id: int
    name: str
    email: str
    role: str
    phantom: bool
    timeline_algorithm: TimelineAlgorithm | None = Field(None, alias="timelineAlgorithm")
    invitation_key: str | None = Field(None, alias="invitationKey")
    confirmed: bool | None = None
    sent_at: datetime | None = Field(None, alias="sentAt")
    confirmed_at: datetime | None = Field(None, alias="confirmedAt")


class UserInvitationsIndexResponse(BaseModel):
    """The response object for the user invitations index endpoint."""

    invitations: list[UserInvitation]
    permissions: ManageCourseUsersPermissions
    manage_course_users_data: ManageCourseUsersSharedData = Field(..., alias="manageCourseUsersData")


class InvitationResult(BaseModel):
    """
    Represents the structured result of an invitation job.
    Corresponds to `InvitationResult` in TypeScript.
    """

    duplicate_users: list[CourseUser] | None = Field(None, alias="duplicateUsers")
    existing_course_users: list[CourseUser] | None = Field(None, alias="existingCourseUsers")
    existing_invitations: list[UserInvitation] | None = Field(None, alias="existingInvitations")
    new_course_users: list[CourseUser] | None = Field(None, alias="newCourseUsers")
    new_invitations: list[UserInvitation] | None = Field(None, alias="newInvitations")


class InviteResponse(BaseModel):
    """The response object after submitting an invitation request."""

    new_invitations: int = Field(..., alias="newInvitations")
    invitation_result: InvitationResult = Field(..., alias="invitationResult")

    @field_validator("invitation_result", mode="before")
    @classmethod
    def parse_json_string(cls: type["InviteResponse"], value: Any) -> Any:
        """
        The API returns invitationResult as a JSON string, so we need to parse it.
        """
        if isinstance(value, str):
            return json.loads(value)
        return value


class CourseRegistrationKeyResponse(BaseModel):
    course_registration_key: str = Field(..., alias="courseRegistrationKey")


class ResendAllResponse(BaseModel):
    invitations: list[UserInvitation]


class IndividualInvite(BaseModel):
    """
    Represents the data for a single user to be invited via a form.
    Corresponds to `IndividualInvite` in TypeScript.
    """

    name: str
    email: str
    role: CourseUserRoles = "student"
    phantom: bool = False
    timeline_algorithm: TimelineAlgorithm | None = Field(alias="timelineAlgorithm", default=None)


class InvitationsFormPayload(BaseModel):
    """
    The main payload containing a list of users to invite via form.
    Corresponds to `InvitationsPostData` in TypeScript.
    """

    invitations_attributes: list[IndividualInvite]
