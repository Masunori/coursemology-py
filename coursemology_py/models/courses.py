from datetime import datetime
from typing import Any, Literal  # Import Dict

from pydantic import BaseModel, Field

# Import nested models from other modules
from coursemology_py.models.course.announcements import Announcement
from coursemology_py.models.course.users import CourseUser

# --- Type Aliases and Enums ---
Progress = Literal["not_started", "in_progress"]

# --- Nested/Shared Models ---


class CoursePermissions(BaseModel):
    """Permissions for the top-level courses component."""

    can_create: bool = Field(..., alias="canCreate")
    is_current_user: bool = Field(..., alias="isCurrentUser")


class CourseDataPermissions(BaseModel):
    """Permissions within a specific course."""

    is_current_course_user: bool = Field(..., alias="isCurrentCourseUser")
    can_manage: bool = Field(..., alias="canManage")


class RoleRequest(BaseModel):
    """Represents a pending role request for the user."""

    id: int
    role: str
    organization: str
    redirect_path: str = Field(..., alias="redirectPath")


class CourseLogo(BaseModel):
    """Represents the URL for a course's logo."""

    url: str | None = None


class RegistrationInfo(BaseModel):
    """Information about the user's registration status for a course."""

    is_display_code_form: bool = Field(..., alias="isDisplayCodeForm")
    is_invited: bool = Field(..., alias="isInvited")
    enrol_request_id: int | None = Field(None, alias="enrolRequestId")
    is_enrollable: bool = Field(..., alias="isEnrollable")


class TimeInfo(BaseModel):
    is_fixed: bool = Field(..., alias="isFixed")
    effective_time: datetime | None = Field(None, alias="effectiveTime")
    reference_time: datetime | None = Field(None, alias="referenceTime")


class TodoData(BaseModel):
    """Represents a single 'todo' item for the user."""

    id: int
    item_actable_id: int = Field(..., alias="itemActableId")
    item_actable_title: str = Field(..., alias="itemActableTitle")
    is_personal_time: bool = Field(..., alias="isPersonalTime")
    start_time_info: TimeInfo = Field(..., alias="startTimeInfo")
    end_time_info: TimeInfo = Field(..., alias="endTimeInfo")
    progress: Progress
    item_actable_specific_id: int = Field(..., alias="itemActableSpecificId")
    can_access: bool | None = None
    can_attempt: bool | None = None


# --- Main Data Models ---


class CourseListData(BaseModel):
    """Represents a single course in a list."""

    id: int
    title: str
    description: str
    logo_url: str | None = Field(None, alias="logoUrl")
    start_at: datetime = Field(..., alias="startAt")


class CourseData(CourseListData):
    """
    Represents the detailed data for a single fetched course.
    This model captures the two possible structures for the response.
    """

    # Case 1: User is NOT enrolled
    registration_info: RegistrationInfo | None = Field(None, alias="registrationInfo")
    instructors: list[CourseUser] | None = None

    # Case 2: User IS enrolled
    currently_active_announcements: list[Announcement] | None = Field(None, alias="currentlyActiveAnnouncements")
    assessment_todos: list[TodoData] | None = Field(None, alias="assessmentTodos")
    video_todos: list[TodoData] | None = Field(None, alias="videoTodos")
    survey_todos: list[TodoData] | None = Field(None, alias="surveyTodos")

    # Common fields
    notifications: list[dict[str, Any]]
    permissions: CourseDataPermissions


class CoursesIndexResponse(BaseModel):
    """The response object for the courses index endpoint."""

    courses: list[CourseListData]
    instance_user_role_request: RoleRequest | None = Field(None, alias="instanceUserRoleRequest")
    permissions: CoursePermissions


class CourseFetchResponse(BaseModel):
    course: CourseData


class SidebarNode(BaseModel):
    id: str
    key: str
    label: str
    type: str
    weight: int
    url: str | None = None
    children: list["SidebarNode"] = []


class SidebarSettings(BaseModel):
    show_my_students: bool = Field(..., alias="showMyStudents")


class CourseLayoutData(BaseModel):
    nodes: list[SidebarNode]
    settings: SidebarSettings


class CourseCreatePayload(BaseModel):
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None


class CourseCreateResponse(BaseModel):
    id: int
    title: str


# Rebuild model to resolve forward reference
SidebarNode.model_rebuild()
