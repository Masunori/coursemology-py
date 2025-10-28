from datetime import datetime

from pydantic import BaseModel, Field

# --- Models for Standard EXP Disbursement ---


class DisbursementCourseUser(BaseModel):
    """Represents a user in the standard disbursement context."""

    id: int
    name: str
    group_ids: list[int] = Field(..., alias="groupIds")


class DisbursementCourseGroup(BaseModel):
    """Represents a group in the standard disbursement context."""

    id: int
    name: str


class DisbursementIndexResponse(BaseModel):
    """The response for the main disbursement index endpoint."""

    course_groups: list[DisbursementCourseGroup] = Field(..., alias="courseGroups")
    course_users: list[DisbursementCourseUser] = Field(..., alias="courseUsers")


class DisbursementRecordPayload(BaseModel):
    """Represents the points awarded to a single user in a disbursement."""

    points_awarded: int
    course_user_id: int


class DisbursementPayload(BaseModel):
    """Represents the main payload for creating a standard disbursement."""

    reason: str | None = None
    experience_points_records_attributes: list[DisbursementRecordPayload]


class DisbursementCreateResponse(BaseModel):
    """The response after successfully creating a disbursement."""

    count: int


# --- Models for Forum EXP Disbursement ---


class ForumDisbursementFilters(BaseModel):
    """Represents the filter settings for a forum disbursement."""

    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    weekly_cap: int = Field(..., alias="weeklyCap")


class ForumDisbursementUser(BaseModel):
    """Represents a user in the forum disbursement context."""

    id: int
    name: str
    level: int
    exp: int
    post_count: int = Field(..., alias="postCount")
    vote_tally: int = Field(..., alias="voteTally")
    points: int


class ForumDisbursementIndexResponse(BaseModel):
    """The response for the forum disbursement index endpoint."""

    filters: ForumDisbursementFilters
    forum_users: list[ForumDisbursementUser] = Field(..., alias="forumUsers")


class ForumDisbursementPayload(DisbursementPayload):
    """
    Represents the main payload for creating a forum disbursement.
    It extends the standard payload with forum-specific fields.
    """

    start_time: datetime
    end_time: datetime
    weekly_cap: int
