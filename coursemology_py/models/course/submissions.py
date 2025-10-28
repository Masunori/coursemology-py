from datetime import datetime
from typing import Any, Literal, Union, Annotated

from pydantic import BaseModel, Field

# --- Type Aliases and Enums ---
SubmissionStatus = Literal["attempting", "submitted", "graded", "published"]

# --- Nested/Shared Models ---

class SubmissionListDataPermissions(BaseModel):
    can_see_grades: bool = Field(..., alias="canSeeGrades")
    can_grade: bool = Field(..., alias="canGrade")

class TeachingStaffInfo(BaseModel):
    teaching_staff_id: int = Field(..., alias="teachingStaffId")
    teaching_staff_name: str = Field(..., alias="teachingStaffName")

class FilterOption(BaseModel):
    id: int
    title: str | None = None
    name: str | None = None

class SubmissionsTabData(BaseModel):
    my_students_pending_count: int | None = Field(None, alias="myStudentsPendingCount")
    all_students_pending_count: int | None = Field(None, alias="allStudentsPendingCount")
    categories: list[FilterOption]

class SubmissionsFilterData(BaseModel):
    assessments: list[FilterOption]
    groups: list[FilterOption]
    users: list[FilterOption]

# --- Top-Level Submissions Models ---

class TopLevelSubmission(BaseModel):
    id: int
    course_user_id: int = Field(..., alias="courseUserId")
    course_user_name: str = Field(..., alias="courseUserName")
    assessment_id: int = Field(..., alias="assessmentId")
    assessment_title: str = Field(..., alias="assessmentTitle")
    submitted_at: datetime | None = Field(None, alias="submittedAt")
    status: SubmissionStatus
    teaching_staff: list[TeachingStaffInfo] | None = Field(None, alias="teachingStaff")
    current_grade: str | None = Field(None, alias="currentGrade")
    is_graded_not_published: bool | None = Field(None, alias="isGradedNotPublished")
    points_awarded: int | None = Field(None, alias="pointsAwarded")
    max_grade: str = Field(..., alias="maxGrade")
    permissions: SubmissionListDataPermissions

class TopLevelSubmissionsMetadata(BaseModel):
    is_gamified: bool = Field(..., alias="isGamified")
    submission_count: int = Field(..., alias="submissionCount")
    tabs: SubmissionsTabData
    filter: SubmissionsFilterData

class TopLevelSubmissionsPermissions(BaseModel):
    can_manage: bool = Field(..., alias="canManage")
    is_teaching_staff: bool = Field(..., alias="isTeachingStaff")

class TopLevelSubmissionsIndexResponse(BaseModel):
    submissions: list[TopLevelSubmission]
    meta_data: TopLevelSubmissionsMetadata = Field(..., alias="metaData")
    permissions: TopLevelSubmissionsPermissions

# --- Assessment-Specific Submissions Models ---

class SubmissionUserInfo(BaseModel):
    id: int
    name: str

class AssessmentSubmission(BaseModel):
    id: int | None = None
    workflow_state: str = Field(..., alias="workflowState")
    grade: int | None = None
    points_awarded: int | None = Field(None, alias="pointsAwarded")
    submitted_at: datetime | None = Field(None, alias="submittedAt")
    course_user: SubmissionUserInfo = Field(..., alias="courseUser")

class AssessmentSubmissionsMetadata(BaseModel):
    title: str
    autograded: bool
    maximum_grade: float | None = Field(None, alias="maximumGrade")

class AssessmentSubmissionsIndexResponse(BaseModel):
    submissions: list[AssessmentSubmission]
    assessment: AssessmentSubmissionsMetadata

# --- Base Answer Models ---

class AnswerGrading(BaseModel):
    id: int
    grade: float | None = None

class BaseAnswerInfo(BaseModel):
    id: int
    question_id: int = Field(..., alias="questionId")
    created_at: datetime = Field(..., alias="createdAt")
    client_version: int | None = Field(None, alias="clientVersion")
    grading: AnswerGrading

# --- Programming Answer Models ---

class ProgrammingFile(BaseModel):
    id: int
    filename: str
    content: str = ""
    highlighted_content: str | None = Field(None, alias="highlightedContent")

class ProgrammingAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int
    files_attributes: list[ProgrammingFile] = Field(..., alias="files_attributes")

class ProgrammingTestCases(BaseModel):
    can_read_tests: bool = Field(..., alias="canReadTests")

class ProgrammingExplanation(BaseModel):
    correct: bool | None = None
    explanations: list[str] = Field(default_factory=list)

class ProgrammingAnswerInfo(BaseAnswerInfo):
    question_type: Literal["Programming"] = Field(..., alias="questionType")
    fields: ProgrammingAnswerFields
    test_cases: ProgrammingTestCases = Field(..., alias="testCases")
    explanation: ProgrammingExplanation
    latest_answer: 'ProgrammingAnswerInfo | None' = Field(None, alias="latestAnswer")

# --- MCQ/MRQ Answer Models ---

class McqMrqAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int
    option_ids: list[int] = Field(default_factory=list, alias="optionIds")

class McqMrqExplanation(BaseModel):
    correct: bool | None = None
    explanations: list[str] = Field(default_factory=list)

class McqAnswerInfo(BaseAnswerInfo):
    question_type: Literal["MultipleChoice"] = Field(..., alias="questionType")
    fields: McqMrqAnswerFields
    explanation: McqMrqExplanation

class MrqAnswerInfo(BaseAnswerInfo):
    question_type: Literal["MultipleResponse"] = Field(..., alias="questionType")
    fields: McqMrqAnswerFields
    explanation: McqMrqExplanation

# --- Text Response Answer Models ---

class TextResponseAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int
    answer_text: str = Field(default="", alias="answerText")

class TextResponseExplanation(BaseModel):
    correct: bool | None = None
    explanations: list[str] = Field(default_factory=list)

class TextResponseAttachment(BaseModel):
    id: str
    name: str

class TextResponseAnswerInfo(BaseAnswerInfo):
    question_type: Literal["TextResponse"] = Field(..., alias="questionType")
    fields: TextResponseAnswerFields
    explanation: TextResponseExplanation
    attachments: list[TextResponseAttachment] = Field(default_factory=list)

# --- File Upload Answer Models ---

class FileUploadAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int

class FileUploadAnswerInfo(BaseAnswerInfo):
    question_type: Literal["FileUpload"] = Field(..., alias="questionType")
    fields: FileUploadAnswerFields
    explanation: TextResponseExplanation
    attachments: list[TextResponseAttachment] = Field(default_factory=list)

# --- Voice Response Answer Models ---

class VoiceResponseFile(BaseModel):
    url: str | None = None
    name: str = ""

class VoiceResponseAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int
    file: VoiceResponseFile

class VoiceResponseAnswerInfo(BaseAnswerInfo):
    question_type: Literal["VoiceResponse"] = Field(..., alias="questionType")
    fields: VoiceResponseAnswerFields
    explanation: TextResponseExplanation

# --- Scribing Answer Models ---

class ScribingAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int

class Scribble(BaseModel):
    content: str
    creator_name: str = Field(..., alias="creatorName")
    creator_id: int = Field(..., alias="creatorId")

class ScribingAnswerData(BaseModel):
    image_url: str = Field(..., alias="imageUrl")
    user_id: int = Field(..., alias="userId")
    answer_id: int = Field(..., alias="answerId")
    scribbles: list[Scribble] = Field(default_factory=list)

class ScribingAnswerInfo(BaseAnswerInfo):
    question_type: Literal["Scribing"] = Field(..., alias="questionType")
    fields: ScribingAnswerFields
    explanation: TextResponseExplanation
    scribing_answer: ScribingAnswerData | None = Field(None, alias="scribingAnswer")

# --- Forum Post Response Answer Models ---

class ForumPostResponseAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int
    answer_text: str = Field(default="", alias="answerText")
    selected_post_packs: list[dict[str, str | int | bool]] = Field(default_factory=list, alias="selectedPostPacks")

class ForumPostResponseAnswerInfo(BaseAnswerInfo):
    question_type: Literal["ForumPostResponse"] = Field(..., alias="questionType")
    fields: ForumPostResponseAnswerFields
    explanation: TextResponseExplanation

# --- Rubric-Based Response Answer Models ---

class RubricBasedResponseAnswerFields(BaseModel):
    question_id: int = Field(..., alias="questionId")
    id: int
    answer_text: str = Field(default="", alias="answerText")

class RubricBasedResponseAnswerInfo(BaseAnswerInfo):
    question_type: Literal["RubricBasedResponse"] = Field(..., alias="questionType")
    fields: RubricBasedResponseAnswerFields
    explanation: TextResponseExplanation

# --- Discriminated Union (Fixed) ---

# Apply discriminator to the union type, not the list
AnyAnswerInfo = Annotated[
    Union[
        ProgrammingAnswerInfo,
        McqAnswerInfo,
        MrqAnswerInfo,
        TextResponseAnswerInfo,
        FileUploadAnswerInfo,
        VoiceResponseAnswerInfo,
        ScribingAnswerInfo,
        ForumPostResponseAnswerInfo,
        RubricBasedResponseAnswerInfo,
    ],
    Field(discriminator='question_type')
]

# --- Submission Edit Models ---

class SubmissionInfo(BaseModel):
    id: int
    can_grade: bool = Field(..., alias="canGrade")
    can_update: bool = Field(..., alias="canUpdate")
    is_creator: bool = Field(..., alias="isCreator")
    is_student: bool = Field(..., alias="isStudent")
    workflow_state: str = Field(..., alias="workflowState")
    submitter: dict[str, str | int]
    bonus_end_at: datetime | None = Field(None, alias="bonusEndAt")
    due_at: datetime | None = Field(None, alias="dueAt")
    attempted_at: datetime | None = Field(None, alias="attemptedAt")
    submitted_at: datetime | None = Field(None, alias="submittedAt")
    maximum_grade: float = Field(..., alias="maximumGrade")
    show_public_test_cases_output: bool | None = Field(None, alias="showPublicTestCasesOutput")
    show_stdout_and_stderr: bool | None = Field(None, alias="showStdoutAndStderr")
    late: bool | None = None
    base_points: int = Field(..., alias="basePoints")
    bonus_points: int = Field(..., alias="bonusPoints")
    points_awarded: int | None = Field(None, alias="pointsAwarded")

class AssessmentInfo(BaseModel):
    category_id: int = Field(..., alias="categoryId")
    tab_id: int = Field(..., alias="tabId")
    title: str
    description: str
    autograded: bool
    skippable: bool
    show_mcq_mrq_solution: bool = Field(..., alias="showMcqMrqSolution")
    show_rubric_to_students: bool = Field(..., alias="showRubricToStudents")
    time_limit: int | None = Field(None, alias="timeLimit")
    delayed_grade_publication: bool = Field(..., alias="delayedGradePublication")
    tabbed_view: bool = Field(..., alias="tabbedView")
    show_private: bool = Field(..., alias="showPrivate")
    allow_partial_submission: bool = Field(..., alias="allowPartialSubmission")
    show_mcq_answer: bool = Field(..., alias="showMcqAnswer")
    show_evaluation: bool = Field(..., alias="showEvaluation")
    question_ids: list[int] = Field(..., alias="questionIds")
    password_protected: bool = Field(..., alias="passwordProtected")
    gamified: bool
    is_koditsu_enabled: bool = Field(..., alias="isKoditsuEnabled")
    files: list[dict[str, str | int]] = Field(default_factory=list)
    is_codaveri_enabled: bool = Field(..., alias="isCodaveriEnabled")

class QuestionInfo(BaseModel):
    id: int
    description: str
    maximum_grade: float = Field(..., alias="maximumGrade")
    can_view_history: bool = Field(..., alias="canViewHistory")
    type: str
    language: str | None = None
    editor_mode: str | None = Field(None, alias="editorMode")
    file_submission: bool | None = Field(None, alias="fileSubmission")
    autogradable: bool | None = None
    is_codaveri: bool | None = Field(None, alias="isCodaveri")
    live_feedback_enabled: bool | None = Field(None, alias="liveFeedbackEnabled")
    question_number: int = Field(..., alias="questionNumber")
    question_title: str = Field(..., alias="questionTitle")
    answer_id: int | None = Field(None, alias="answerId")
    topic_id: int | None = Field(None, alias="topicId")
    submission_question_id: int | None = Field(None, alias="submissionQuestionId")

class TopicInfo(BaseModel):
    id: int
    submission_question_id: int = Field(..., alias="submissionQuestionId")
    question_id: int = Field(..., alias="questionId")
    post_ids: list[int] = Field(..., alias="postIds")

class AnnotationInfo(BaseModel):
    file_id: int = Field(..., alias="fileId")
    topics: list[dict[str, str | int]] = Field(default_factory=list)

class AnswerHistory(BaseModel):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    current_answer: bool = Field(..., alias="currentAnswer")
    workflow_state: str = Field(..., alias="workflowState")

class QuestionHistory(BaseModel):
    id: int
    answers: list[AnswerHistory] = Field(default_factory=list)

class SubmissionEditData(BaseModel):
    submission: SubmissionInfo
    assessment: AssessmentInfo
    questions: list[QuestionInfo]
    answers: list[AnyAnswerInfo]
    topics: list[TopicInfo]
    annotations: list[AnnotationInfo]
    posts: list[dict[str, str | int | bool]] = Field(default_factory=list)
    history: dict[str, list[QuestionHistory]] = Field(default_factory=dict)
    get_help_counts: list[dict[str, str | int]] = Field(default_factory=list, alias="getHelpCounts")

# --- Other Models ---

class AnswerGradeUpdate(BaseModel):
    """Individual answer grade update within a submission."""
    id: int
    grade: str  # API expects string, not int

class SubmissionGradeUpdate(BaseModel):
    """Payload for updating grades in a submission."""
    answers: list[AnswerGradeUpdate]
    draft_points_awarded: int = 0

class ReloadAnswerResponse(BaseModel):
    question_id: int = Field(..., alias="questionId")
    answer_id: int = Field(..., alias="answerId")
    new_answer: dict[str, Any] = Field(..., alias="newAnswer")

class LiveFeedbackThread(BaseModel):
    id: str
    status: str

class LiveFeedbackChat(BaseModel):
    id: str
    token: str
    url: str

class ProgrammingAnnotationPayload(BaseModel):
    line: int
    text: str