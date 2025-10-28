from typing import Literal

from pydantic import BaseModel, Field

# Import nested models from other modules
# from coursemology_py.models.course.assessment.skills import Skill, SkillBranch
# from coursemology_py.models.course.achievements import Achievement


# --- Type Aliases and Enums ---
CourseUserRoles = Literal["student", "teaching_assistant", "manager", "owner", "observer"]
StaffRoles = Literal["teaching_assistant", "manager", "owner", "observer"]
TimelineAlgorithm = Literal["fixed", "fomo", "stragglers", "otot"]


# --- Basic user representations ---
class CourseUserBasicMini(BaseModel):
    id: int
    name: str


class CourseUserBasic(BaseModel):
    id: int
    name: str
    user_url: str | None = Field(None, alias="userUrl")
    image_url: str | None = Field(None, alias="imageUrl")
    role: CourseUserRoles | None = None


# --- Detailed user representations ---
class CourseUser(BaseModel):
    """Corresponds to CourseUserListData in TypeScript."""

    id: int
    # user_id: int = Field(..., alias="userId")
    name: str
    image_url: str | None = Field(None, alias="imageUrl")
    role: CourseUserRoles
    is_phantom: bool | None = Field(None, alias="phantom")
    # name_link: str = Field(..., alias="nameLink")
    timeline_id: int | None = Field(None, alias="referenceTimelineId")
    email: str
    # timeline_algorithm: TimelineAlgorithm | None = Field(None, alias="timelineAlgorithm")


class UserSkill(BaseModel):
    """Corresponds to UserSkillListData in TypeScript."""

    id: int
    branch_id: int | None = Field(None, alias="branchId")
    title: str
    percentage: float
    grade: int
    total_grade: int = Field(..., alias="totalGrade")


class UserSkillBranch(BaseModel):
    """Corresponds to UserSkillBranchListData in TypeScript."""

    id: int
    title: str
    user_skills: list[UserSkill] | None = Field(None, alias="userSkills")


class CourseUserData(CourseUser):
    """
    The most detailed user object, returned by the fetch(user_id) endpoint.
    Corresponds to CourseUserData in TypeScript.
    """

    level: int | None = None
    exp: int | None = None
    # achievements: Optional[List[Achievement]] = None
    experience_points_records_url: str | None = Field(None, alias="experiencePointsRecordsUrl")
    skill_branches: list[UserSkillBranch] | None = Field(None, alias="skillBranches")
    learning_rate: float | None = Field(None, alias="learningRate")
    learning_rate_effective_min: float | None = Field(None, alias="learningRateEffectiveMin")
    learning_rate_effective_max: float | None = Field(None, alias="learningRateEffectiveMax")
    can_read_statistics: bool = Field(..., alias="canReadStatistics")
    time_zone: str | None = Field(None, alias="timeZone")
    # is_manager: bool = Field(..., alias="isManager")
    # managers: list[CourseUserBasic]


# --- Models for API request payloads ---
class UpdateCourseUser(BaseModel):
    """
    Payload for updating a course user.
    Corresponds to UpdateCourseUserPatchData in TypeScript.
    """

    name: str | None = None
    phantom: bool | None = None
    timeline_algorithm: TimelineAlgorithm | None = Field(alias="timeline_algorithm", default=None)
    reference_timeline_id: int | None = None
    role: CourseUserRoles | None = None


# --- Models for API responses ---
class ManageCourseUsersPermissions(BaseModel):
    can_manage_course_users: bool = Field(..., alias="canManageCourseUsers")
    can_manage_enrol_requests: bool = Field(..., alias="canManageEnrolRequests")
    can_manage_personal_times: bool = Field(..., alias="canManagePersonalTimes")
    can_manage_reference_timelines: bool = Field(..., alias="canManageReferenceTimelines")
    can_register_with_code: bool = Field(..., alias="canRegisterWithCode")


class GroupCategory(BaseModel):
    id: int
    name: str


class ManageCourseUsersSharedData(BaseModel):
    requests_count: int = Field(..., alias="requestsCount")
    invitations_count: int = Field(..., alias="invitationsCount")
    # default_timeline_algorithm: TimelineAlgorithm = Field(..., alias="defaultTimelineAlgorithm")


class UsersIndexResponse(BaseModel):
    """Response for index() when as_basic_data is False."""

    users: list[CourseUser]
    permissions: ManageCourseUsersPermissions
    manage_course_users_data: ManageCourseUsersSharedData = Field(..., alias="manageCourseUsersData")


class UsersIndexBasicResponse(BaseModel):
    """Response for index() when as_basic_data is True."""

    users: list[CourseUserBasic]
    permissions: ManageCourseUsersPermissions
    manage_course_users_data: ManageCourseUsersSharedData = Field(..., alias="manageCourseUsersData")


class StudentsIndexResponse(UsersIndexResponse):
    timelines: dict[str, str] | None = None


class UserFetchResponse(BaseModel):
    user: CourseUserData
