from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# --- Type Aliases and Enums ---
WorkflowState = Literal["attempting", "submitted", "graded", "published"]

# --- Models for CourseStatisticsAPI ---


class StatisticsIndexData(BaseModel):
    """Data from the main statistics index endpoint."""

    codaveri_component_enabled: bool = Field(..., alias="codaveriComponentEnabled")


class StudentStatistic(BaseModel):
    """Statistics for a single student."""

    id: int
    name: str
    is_phantom: bool = Field(..., alias="isPhantom")
    role: str
    level: int
    experience_points: int = Field(..., alias="experiencePoints")
    video_percent_watched: float = Field(..., alias="videoPercentWatched")


class StudentsStatistics(BaseModel):
    """Container for a list of student statistics."""

    students: list[StudentStatistic]


class StaffStatistic(BaseModel):
    """Statistics for a single staff member."""

    id: int
    name: str


class StaffStatistics(BaseModel):
    """Container for a list of staff statistics."""

    staff: list[StaffStatistic]


class ProgressionItem(BaseModel):
    """Represents a single item in the course progression statistics."""

    id: int
    title: str
    item_type: str = Field(..., alias="itemType")
    path: str
    completed_items_count: int = Field(..., alias="completedItemsCount")
    total_items_count: int = Field(..., alias="totalItemsCount")


class CourseProgressionStatistics(BaseModel):
    """Container for course progression statistics."""

    progression: list[ProgressionItem]


class PerformanceMetric(BaseModel):
    """Represents a single metric in the course performance statistics."""

    id: int
    title: str
    average_marks: float | None = Field(None, alias="averageMarks")
    std_deviation: float | None = Field(None, alias="stdDeviation")


class CoursePerformanceStatistics(BaseModel):
    """Container for course performance statistics."""

    performance: list[PerformanceMetric]


class AssessmentStatistic(BaseModel):
    """Represents statistics for a single assessment."""

    id: int
    title: str
    start_at: datetime = Field(..., alias="startAt")
    end_at: datetime | None = Field(None, alias="endAt")
    average_time: str = Field(..., alias="averageTime")
    submission_rate: float = Field(..., alias="submissionRate")


class AssessmentsStatistics(BaseModel):
    """Container for assessment statistics."""

    assessments: list[AssessmentStatistic]


class CourseGetHelpActivity(BaseModel):
    user_id: int
    activity_count: int


# --- Models for UserStatisticsAPI ---


class LearningRateRecord(BaseModel):
    """Represents a single learning rate record for a user."""

    id: int
    learning_rate_alpha: float = Field(..., alias="learningRateAlpha")
    total_exp: int = Field(..., alias="totalExp")
    exp_awarded: int = Field(..., alias="expAwarded")
    created_at: datetime = Field(..., alias="createdAt")


class LearningRateRecordsData(BaseModel):
    """Container for learning rate records."""

    records: list[LearningRateRecord]
    is_phantom: bool = Field(..., alias="isPhantom")


# --- Models for AnswerStatisticsAPI ---


class QuestionDetail(BaseModel):
    id: int
    type: str
    title: str
    description: str


class AnswerDetail(BaseModel):
    id: int
    grade: float | None = None


class AnswerDataWithQuestion(BaseModel):
    answer: AnswerDetail
    question: QuestionDetail


# --- Models for AssessmentStatisticsAPI ---


class UserInfo(BaseModel):
    id: int
    name: str


class StudentInfo(UserInfo):
    is_phantom: bool = Field(..., alias="isPhantom")
    role: Literal["student"]
    email: str | None = None


class AttemptInfo(BaseModel):
    last_attempt_answer_id: int = Field(..., alias="lastAttemptAnswerId")
    is_autograded: bool = Field(..., alias="isAutograded")
    attempt_count: int = Field(..., alias="attemptCount")
    correct: bool | None = None


class AnswerInfo(BaseModel):
    last_attempt_answer_id: int = Field(..., alias="lastAttemptAnswerId")
    grade: float
    maximum_grade: float = Field(..., alias="maximumGrade")


class GroupInfo(BaseModel):
    name: str


class MainSubmissionInfo(BaseModel):
    id: int
    course_user: StudentInfo = Field(..., alias="courseUser")
    workflow_state: WorkflowState | None = Field(None, alias="workflowState")
    submitted_at: datetime | None = Field(None, alias="submittedAt")
    end_at: datetime | None = Field(None, alias="endAt")
    total_grade: float | None = Field(None, alias="totalGrade")
    maximum_grade: float | None = Field(None, alias="maximumGrade")
    attempt_status: list[AttemptInfo] | None = Field(None, alias="attemptStatus")
    answers: list[AnswerInfo] | None = None
    grader: UserInfo | None = None
    groups: list[GroupInfo]


class MainAssessmentInfo(BaseModel):
    id: int
    title: str
    start_at: datetime | None = Field(None, alias="startAt")
    end_at: datetime | None = Field(None, alias="endAt")
    maximum_grade: float = Field(..., alias="maximumGrade")
    url: str
    is_autograded: bool = Field(..., alias="isAutograded")
    question_count: int = Field(..., alias="questionCount")
    question_ids: list[int] = Field(..., alias="questionIds")
    live_feedback_enabled: bool = Field(..., alias="liveFeedbackEnabled")


class AncestorInfo(BaseModel):
    id: int
    title: str
    course_title: str = Field(..., alias="courseTitle")


class AncestorSubmissionInfo(BaseModel):
    id: int
    course_user: StudentInfo = Field(..., alias="courseUser")
    workflow_state: WorkflowState = Field(..., alias="workflowState")
    submitted_at: datetime | None = Field(None, alias="submittedAt")
    end_at: datetime | None = Field(None, alias="endAt")
    total_grade: float | None = Field(None, alias="totalGrade")


class AncestorAssessmentInfo(BaseModel):
    id: int
    title: str
    start_at: datetime | None = Field(None, alias="startAt")
    end_at: datetime | None = Field(None, alias="endAt")
    maximum_grade: float = Field(..., alias="maximumGrade")
    url: str


class AncestorAssessmentStats(BaseModel):
    assessment: AncestorAssessmentInfo
    submissions: list[AncestorSubmissionInfo]


class AssessmentLiveFeedbackData(BaseModel):
    grade: float
    grade_diff: float = Field(..., alias="grade_diff")
    messages_sent: int = Field(..., alias="messages_sent")
    word_count: int = Field(..., alias="word_count")


class AssessmentLiveFeedbackStatistics(BaseModel):
    course_user: StudentInfo = Field(..., alias="courseUser")
    groups: list[GroupInfo]
    workflow_state: WorkflowState | None = Field(None, alias="workflowState")
    submission_id: int | None = Field(None, alias="submissionId")
    live_feedback_data: list[AssessmentLiveFeedbackData] = Field(..., alias="liveFeedbackData")
    question_ids: list[int] = Field(..., alias="questionIds")
    total_metric_count: int | None = Field(None, alias="totalMetricCount")


class LiveFeedbackMessageFile(BaseModel):
    id: int
    filename: str
    content: str
    language: str
    editor_mode: str = Field(..., alias="editorMode")


class LiveFeedbackMessageOption(BaseModel):
    option_id: int = Field(..., alias="optionId")
    option_type: Literal["suggestion", "fix"] = Field(..., alias="optionType")


class LiveFeedbackChatMessage(BaseModel):
    id: int
    content: str
    created_at: datetime = Field(..., alias="createdAt")
    creator_id: int = Field(..., alias="creatorId")
    is_error: bool = Field(..., alias="isError")
    files: list[LiveFeedbackMessageFile]
    options: list[LiveFeedbackMessageOption]
    option_id: int = Field(..., alias="optionId")


class LiveFeedbackQuestionInfo(BaseModel):
    id: int
    title: str
    description: str


class LiveFeedbackHistoryState(BaseModel):
    messages: list[LiveFeedbackChatMessage]
    question: LiveFeedbackQuestionInfo
    end_of_conversation_files: list[LiveFeedbackMessageFile] | None = Field(None, alias="endOfConversationFiles")
