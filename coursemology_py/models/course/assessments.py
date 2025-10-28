from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# Import a base Question model to be used in lists.
# A full implementation would use a discriminated union like in the answers model.
from coursemology_py.models.course.assessment.questions import Question as BaseQuestion

# --- Type Aliases and Enums ---
AssessmentStatus = Literal["locked", "attempting", "submitted", "open", "unavailable"]

# --- Nested/Shared Models ---


class PersonalTimeData(BaseModel):
    is_fixed: bool = Field(..., alias="isFixed")
    effective_time: datetime | None = Field(None, alias="effectiveTime")
    reference_time: datetime | None = Field(None, alias="referenceTime")


class AssessmentActionsData(BaseModel):
    status: AssessmentStatus
    action_button_url: str | None = Field(None, alias="actionButtonUrl")
    monitoring_url: str | None = Field(None, alias="monitoringUrl")
    statistics_url: str | None = Field(None, alias="statisticsUrl")
    plagiarism_url: str | None = Field(None, alias="plagiarismUrl")
    submissions_url: str | None = Field(None, alias="submissionsUrl")
    edit_url: str | None = Field(None, alias="editUrl")
    delete_url: str | None = Field(None, alias="deleteUrl")


class AchievementBadgeData(BaseModel):
    url: str
    badge_url: str | None = Field(None, alias="badgeUrl")
    title: str


class AssessmentPermissions(BaseModel):
    can_attempt: bool | None = Field(default=None, alias="canAttempt")
    can_manage: bool | None = Field(default=None, alias="canManage")
    can_observe: bool | None = Field(default=None, alias="canObserve")
    can_invite_to_koditsu: bool | None = Field(default=None, alias="canInviteToKoditsu")


class Requirement(BaseModel):
    title: str
    satisfied: bool | None = None


class Unlock(BaseModel):
    description: str
    title: str
    url: str


class AssessmentFile(BaseModel):
    id: int
    name: str
    url: str | None = None


class NewQuestionBuilder(BaseModel):
    type: str  # Corresponds to keyof typeof QuestionType
    url: str


class AssessmentTabInfo(BaseModel):
    id: int
    title: str


class AssessmentCategoryInfo(BaseModel):
    id: int
    title: str


class SkillOption(BaseModel):
    id: int
    title: str


class RedirectResponse(BaseModel):
    redirect_url: str = Field(..., alias="redirectUrl")


class MonitoringData(BaseModel):
    sessions: list[dict[str, Any]]
    monitors: list[dict[str, Any]]


class SebPayload(BaseModel):
    config_key_hash: str = Field(..., alias="config_key_hash")
    url: str


# --- Main Data Models ---


class AssessmentListData(AssessmentActionsData):
    """Represents a single assessment in a list."""

    id: int
    title: str
    password_protected: bool = Field(..., alias="passwordProtected")
    published: bool
    autograded: bool
    has_personal_times: bool = Field(..., alias="hasPersonalTimes")
    affects_personal_times: bool = Field(..., alias="affectsPersonalTimes")
    url: str
    condition_satisfied: bool = Field(..., alias="conditionSatisfied")
    start_at: PersonalTimeData = Field(..., alias="startAt")
    time_limit: int | None = Field(None, alias="timeLimit")
    is_start_time_begin: bool = Field(..., alias="isStartTimeBegin")
    is_koditsu_assessment_enabled: bool | None = Field(None, alias="isKoditsuAssessmentEnabled")
    base_exp: int | None = Field(None, alias="baseExp")
    time_bonus_exp: int | None = Field(None, alias="timeBonusExp")
    bonus_end_at: PersonalTimeData | None = Field(None, alias="bonusEndAt")
    end_at: PersonalTimeData | None = Field(None, alias="endAt")
    has_todo: bool | None = Field(None, alias="hasTodo")
    is_bonus_ended: bool | None = Field(None, alias="isBonusEnded")
    is_end_time_passed: bool | None = Field(None, alias="isEndTimePassed")
    remaining_conditionals_count: int | None = Field(None, alias="remainingConditionalsCount")
    top_conditionals: list[AchievementBadgeData] | None = Field(None, alias="topConditionals")


class AssessmentData(AssessmentActionsData):
    """Represents the detailed data for a single fetched assessment."""

    id: int
    title: str
    tab_title: str = Field(..., alias="tabTitle")
    tab_url: str = Field(..., alias="tabUrl")
    description: str | None = Field(default=None, alias="description")
    autograded: bool
    start_at: PersonalTimeData = Field(..., alias="startAt")
    has_attempts: bool = Field(..., alias="hasAttempts")
    permissions: AssessmentPermissions
    requirements: list[Requirement]
    index_url: str = Field(..., alias="indexUrl")
    end_at: PersonalTimeData | None = Field(None, alias="endAt")
    has_todo: bool | None = Field(None, alias="hasTodo")
    time_limit: int | None = Field(None, alias="timeLimit")
    unlocks: list[Unlock] | None = None
    base_exp: int | None = Field(None, alias="baseExp")
    time_bonus_exp: int | None = Field(None, alias="timeBonusExp")
    bonus_end_at: PersonalTimeData | None = Field(None, alias="bonusEndAt")
    will_start_at: str | None = Field(None, alias="willStartAt")
    materials_disabled: bool | None = Field(None, alias="materialsDisabled")
    components_settings_url: str | None = Field(None, alias="componentsSettingsUrl")
    files: list[AssessmentFile] | None = None
    live_feedback_enabled: bool | None = Field(None, alias="liveFeedbackEnabled")
    is_koditsu_assessment_enabled: bool | None = Field(None, alias="isKoditsuAssessmentEnabled")
    is_synced_with_koditsu: bool | None = Field(None, alias="isSyncedWithKoditsu")
    is_student: bool = Field(..., alias="isStudent")
    show_mcq_mrq_solution: bool | None = Field(None, alias="showMcqMrqSolution")
    show_rubric_to_students: bool | None = Field(None, alias="showRubricToStudents")
    graded_test_cases: str | None = Field(None, alias="gradedTestCases")
    skippable: bool | None = None
    allow_partial_submission: bool | None = Field(None, alias="allowPartialSubmission")
    show_mcq_answer: bool | None = Field(None, alias="showMcqAnswer")
    has_unautogradable_questions: bool | None = Field(None, alias="hasUnautogradableQuestions")
    questions: list[BaseQuestion] | None = None
    new_question_urls: list[NewQuestionBuilder] | None = Field(None, alias="newQuestionUrls")
    generate_question_urls: list[NewQuestionBuilder] | None = Field(None, alias="generateQuestionUrls")


# --- API Response Models ---


class AssessmentsIndexResponse(BaseModel):
    assessments: list[AssessmentListData]


class AssessmentFetchResponse(BaseModel):
    assessment: AssessmentData


class AssessmentUnlockRequirementsResponse(BaseModel):
    requirements: list[str]


class AssessmentEditData(BaseModel):
    assessment: AssessmentData
    categories: list[AssessmentCategoryInfo]


class SkillsOptionsResponse(BaseModel):
    skills: list[SkillOption]


class AssessmentPayload(BaseModel):
    """
    Exhaustive payload for creating an assessment, matching the example request.
    """

    title: str
    description: str = ""
    start_at: datetime
    end_at: datetime | None = None

    # --- Set explicit defaults for all boolean flags ---
    published: bool = False
    autograded: bool = False
    has_todo: bool = True
    skippable: bool = False
    allow_partial_submission: bool = False
    show_mcq_answer: bool = True
    tabbed_view: bool = False
    delayed_grade_publication: bool = False
    password_protected: bool = False
    view_password: str | None = None
    session_password: str | None = None
    show_mcq_mrq_solution: bool = True
    show_rubric_to_students: bool = False
    randomization: bool = False
    block_student_viewing_after_submitted: bool = False
    has_personal_times: bool = False
    affects_personal_times: bool = False
    has_time_limit: bool = False
    time_limit: int | None = None

    bonus_end_at: datetime | None = None
    base_exp: int = 0
    time_bonus_exp: int = 0


class CreateAssessmentPayload(BaseModel):
    """
    Payload specifically for creating an assessment.
    """

    assessment: AssessmentPayload
    category: int
    tab: int


class AssessmentIDResponse(BaseModel):
    id: int
