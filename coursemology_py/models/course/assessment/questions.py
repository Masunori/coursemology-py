# coursemology_py/models/course/assessment/questions.py

from typing import Literal

from pydantic import BaseModel, Field

# --- Type Aliases and Enums ---
QuestionType = Literal[
    "MultipleChoice",
    "MultipleResponse",
    "Programming",
    "TextResponse",
    "FileUpload",
    "Scribing",
    "VoiceResponse",
    "ForumPostResponse",
    "RubricBasedResponse",
]
LanguageMode = Literal["c_cpp", "java", "javascript", "python", "r", "csharp", "golang", "rust", "typescript"]

# --- Base and Shared Models ---


class RedirectWithEditUrl(BaseModel):
    redirect_url: str = Field(..., alias="redirectUrl")
    redirect_edit_url: str = Field(..., alias="redirectEditUrl")


class JustRedirect(BaseModel):
    redirect_url: str = Field(..., alias="redirectUrl")


class Skill(BaseModel):
    id: int
    title: str


class Question(BaseModel):
    """Corresponds to the base QuestionData in TypeScript."""

    id: int
    number: int
    default_title: str = Field(..., alias="defaultTitle")
    title: str | None = None
    unautogradable: bool
    plagiarism_checkable: bool = Field(..., alias="plagiarismCheckable")
    type: str
    is_compatible_with_koditsu: bool | None = Field(default=None, alias="isCompatibleWithKoditsu")
    description: str | None = None
    edit_url: str | None = Field(default=None, alias="editUrl")
    delete_url: str | None = Field(default=None, alias="deleteUrl")


# --- MCQ/MRQ Models ---


class MultipleResponseOption(BaseModel):
    id: int | None = None
    correct: bool
    option: str
    explanation: str | None = None
    weight: int
    ignore_randomization: bool | None = Field(default=None, alias="ignoreRandomization")


class MultipleResponseQuestion(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    staff_only_comments: str | None = Field(default=None, alias="staffOnlyComments")
    maximum_grade: int
    weight: int
    skill_ids: list[int] = Field(default=[], alias="skillIds")
    options: list[MultipleResponseOption]
    skip_grading: bool | None = Field(default=None, alias="skipGrading")
    randomize_options: bool | None = Field(default=None, alias="randomizeOptions")


class QuestionAssessmentPayload(BaseModel):
    skill_ids: list[int] = Field(default=[], alias="skill_ids")


class McqMrqPayload(BaseModel):
    """The correct, flat payload for creating/updating an MCQ/MRQ."""
    title: str
    description: str | None = None
    staff_only_comments: str | None = Field(default=None, alias="staff_only_comments")
    maximum_grade: int
    grading_scheme: Literal["any_correct", "all_correct"] = Field(..., alias="grading_scheme")
    randomize_options: bool | None = Field(default=None, alias="randomize_options")
    skip_grading: bool | None = Field(default=None, alias="skip_grading")
    question_assessment: QuestionAssessmentPayload = Field(default_factory=QuestionAssessmentPayload, alias="question_assessment")
    options_attributes: list[MultipleResponseOption] = Field(..., alias="options_attributes")


class McqMrqPostData(BaseModel):
    question_multiple_response: McqMrqPayload = Field(..., alias="question_multiple_response")


class McqMrqFormData(BaseModel):
    grading_scheme: Literal["any_correct", "all_correct"] = Field(..., alias="gradingScheme")
    question: MultipleResponseQuestion
    allow_randomization: bool = Field(..., alias="allowRandomization")


# --- Text Response Models ---


class TextResponseSolution(BaseModel):
    id: int | None = None
    solution_type: Literal["exact_match", "keyword"] = Field(..., alias="solutionType")
    solution: str
    grade: int
    explanation: str | None = None


class TextResponseQuestion(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    staff_only_comments: str | None = Field(default=None, alias="staffOnlyComments")
    maximum_grade: int
    weight: int
    skill_ids: list[int] = Field(default=[], alias="skillIds")
    is_attachment_required: bool = Field(default=False, alias="isAttachmentRequired")
    allow_attachment: bool
    hide_text: bool
    solutions_attributes: list[TextResponseSolution] | None = Field(default=None, alias="solutions_attributes")


class TextResponseFormData(BaseModel):
    question: TextResponseQuestion
    is_file_upload: bool = Field(..., alias="isFileUpload")


class TextResponsePostData(BaseModel):
    question_text_response: TextResponseQuestion = Field(..., alias="question_text_response")


# --- Programming Models ---


class Language(BaseModel):
    id: int
    name: str
    editor_mode: LanguageMode = Field(..., alias="editorMode")


class TemplateFile(BaseModel):
    id: int | None = None
    filename: str
    content: str


class TestCase(BaseModel):
    id: int | None = None
    test_case_type: Literal["public", "private", "evaluation"] | None = Field(default=None, alias="testCaseType")
    expression: str
    expected: str
    hint: str | None = None


class ProgrammingQuestion(BaseModel):
    id: int | None = None
    title: str
    description: str | None = None
    staff_only_comments: str | None = Field(default=None, alias="staffOnlyComments")
    maximum_grade: int | None = None
    weight: int | None = None
    skill_ids: list[int] = Field(default=[], alias="skillIds")
    language_id: int | None = None
    memory_limit: str | None = Field(default=None, alias="memoryLimit")
    time_limit: str | None = Field(default=None, alias="timeLimit")
    is_codaveri: bool | None = None
    multiple_file_submission: bool | None = Field(default=None, alias="multipleFileSubmission")
    template_files_attributes: list[TemplateFile] | None = Field(default=None, alias="template_files_attributes")
    test_cases_attributes: list[TestCase] | None = Field(default=None, alias="test_cases_attributes")


class ProgrammingFormData(BaseModel):
    question: ProgrammingQuestion
    languages: list[Language]


class ProgrammingPostData(BaseModel):
    question_programming: ProgrammingQuestion = Field(..., alias="question_programming")


class ProgrammingPostStatusData(BaseModel):
    id: int | None = None
    redirect_assessment_url: str | None = Field(default=None, alias="redirectAssessmentUrl")
    redirect_edit_url: str | None = Field(default=None, alias="redirectEditUrl")
    import_job_url: str | None = Field(default=None, alias="importJobUrl")
    message: str | None = None


class PackageImportResultData(BaseModel):
    status: Literal["success", "error"] | None = None
    error: str | None = None
    message: str | None = None


class CodaveriGenerateResponse(BaseModel):
    code: str
    explanation: str


class UpdateQnSettingPayload(BaseModel):
    is_codaveri: bool
