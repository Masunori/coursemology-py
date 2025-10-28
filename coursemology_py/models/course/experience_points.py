from datetime import datetime

from pydantic import BaseModel, Field

from coursemology_py.models.course.users import CourseUserBasic


class ExperiencePointsRecordPermissions(BaseModel):
    """Permissions for a single experience points record."""

    can_update: bool = Field(..., alias="canUpdate")
    can_destroy: bool = Field(..., alias="canDestroy")


class PointsReason(BaseModel):
    """Represents the reason for an EXP award, which can be a link."""

    is_manually_awarded: bool | None = Field(alias="isManuallyAwarded", default=None)
    text: str
    link: str | None = None
    max_exp: int | None = Field(None, alias="maxExp")


class ExperiencePointsRecord(BaseModel):
    """
    Represents a single experience points record with all its details.
    Corresponds to `ExperiencePointsRecordListData` in TypeScript.
    """

    id: int
    student: CourseUserBasic | None = None
    updater: CourseUserBasic
    reason: PointsReason
    points_awarded: int = Field(..., alias="pointsAwarded")
    updated_at: datetime = Field(..., alias="updatedAt")
    permissions: ExperiencePointsRecordPermissions | None = None


class ExperiencePointsNameFilter(BaseModel):
    """Represents a student in the filter dropdown."""

    id: int
    name: str


class ExperiencePointsFilterData(BaseModel):
    """Container for the available filters."""

    course_students: list[ExperiencePointsNameFilter] = Field(..., alias="courseStudents")


class ExperiencePointsRecordsResponse(BaseModel):
    """
    The response object for fetching all EXP records.
    Corresponds to `ExperiencePointsRecords` in TypeScript.
    """

    row_count: int = Field(..., alias="rowCount")
    records: list[ExperiencePointsRecord]
    filters: ExperiencePointsFilterData


class ExperiencePointsRecordsForUserResponse(BaseModel):
    """
    The response object for fetching a single user's EXP records.
    Corresponds to `ExperiencePointsRecordsForUser` in TypeScript.
    """

    row_count: int = Field(..., alias="rowCount")
    records: list[ExperiencePointsRecord]
    student_name: str = Field(..., alias="studentName")


class ExperiencePointsRecordPayload(BaseModel):
    """
    A model representing the data payload for updating an experience points record.
    Corresponds to `UpdateExperiencePointsRecordPatchData` in TypeScript.
    """

    reason: str
    points_awarded: int
