from datetime import datetime
from typing import Any, Literal, Union, Annotated

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
TestCaseType = Literal["public_test", "private_test", "evaluation_test"]
JobStatus = Literal["submitted", "running", "completed", "errored"]

# --- Base and Shared Models ---

class AnswerGradingInfo(BaseModel):
    grade: float | None = None
    grader: dict[str, Any] | None = None

class AnswerBase(BaseModel):
    id: int
    created_at: datetime = Field(..., alias="createdAt")
    question_type: str = Field(..., alias="questionType")
    grading: AnswerGradingInfo
    client_version: int | None = Field(None, alias="clientVersion")

class QuestionBase(BaseModel):
    id: int
    question_title: str = Field(..., alias="questionTitle")
    description: str | None = None
    maximum_grade: str = Field(..., alias="maximumGrade")  # API returns as string
    type: str

class Explanation(BaseModel):
    correct: bool | None = None
    explanations: list[str] = Field(default_factory=list)

# --- Models for MultipleChoice / MultipleResponse ---

class McqMrqOption(BaseModel):
    id: int
    option: str
    correct: bool | None = None

class McqAnswer(AnswerBase):
    question_type: Literal["MultipleChoice", "MultipleResponse"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    option_ids: list[int] = Field(..., alias="optionIds")
    explanation: Explanation
    latest_answer: "McqAnswer | None" = Field(None, alias="latestAnswer")

class McqQuestion(QuestionBase):
    type: Literal["MultipleChoice", "MultipleResponse"]
    options: list[McqMrqOption]

# --- Models for Programming ---

class ProgrammingFile(BaseModel):
    id: int
    filename: str
    content: str
    highlighted_content: str | None = Field(None, alias="highlightedContent")

class TestCaseResult(BaseModel):
    identifier: str | None = None
    expression: str
    expected: str
    output: str | None = None
    passed: bool

class TestCase(BaseModel):
    can_read_tests: bool = Field(..., alias="canReadTests")
    public_test: list[TestCaseResult] | None = Field(None, alias="public_test")
    private_test: list[TestCaseResult] | None = Field(None, alias="private_test")
    evaluation_test: list[TestCaseResult] | None = Field(None, alias="evaluation_test")
    stdout: str | None = None
    stderr: str | None = None

class ProgrammingExplanation(Explanation):
    failure_type: TestCaseType | None = Field(None, alias="failureType")

class AutogradingStatus(BaseModel):
    status: JobStatus
    job_url: str | None = Field(None, alias="jobUrl")
    path: str | None = None

class CodaveriFeedback(BaseModel):
    job_id: str = Field(..., alias="jobId")
    job_status: JobStatus = Field(..., alias="jobStatus")
    job_url: str | None = Field(None, alias="jobUrl")
    error_message: str | None = Field(None, alias="errorMessage")

class AnnotationTopic(BaseModel):
    id: int
    post_ids: list[int] = Field(..., alias="postIds")
    line: str

class Annotation(BaseModel):
    file_id: int = Field(..., alias="fileId")
    topics: list[AnnotationTopic] = Field(default_factory=list)

class PostCreator(BaseModel):
    id: int
    name: str
    user_url: str = Field(..., alias="userUrl")
    image_url: str = Field(..., alias="imageUrl")

class Post(BaseModel):
    id: int
    topic_id: int = Field(..., alias="topicId")
    title: str
    text: str
    creator: PostCreator
    created_at: datetime = Field(..., alias="createdAt")
    can_update: bool = Field(..., alias="canUpdate")
    can_destroy: bool = Field(..., alias="canDestroy")
    is_delayed: bool = Field(..., alias="isDelayed")

class ProgrammingAnswer(AnswerBase):
    question_type: Literal["Programming"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    fields: dict[str, Any]  # Contains files_attributes
    explanation: ProgrammingExplanation
    test_cases: TestCase = Field(..., alias="testCases")
    attempts_left: int | None = Field(None, alias="attemptsLeft")
    autograding: AutogradingStatus | None = None
    codaveri_feedback: CodaveriFeedback | None = Field(None, alias="codaveriFeedback")
    annotations: list[Annotation] = Field(default_factory=list)
    posts: list[Post] = Field(default_factory=list)
    latest_answer: "ProgrammingAnswer | None" = Field(None, alias="latestAnswer")

    @property
    def files(self) -> list[ProgrammingFile]:
        """Extract files from the fields dict for easier access."""
        files_data = self.fields.get("files_attributes", [])
        return [ProgrammingFile.model_validate(f) for f in files_data]

class ProgrammingQuestion(QuestionBase):
    type: Literal["Programming"]
    language: str
    editor_mode: str = Field(..., alias="editorMode")
    file_submission: bool = Field(..., alias="fileSubmission")
    autogradable: bool
    is_codaveri: bool = Field(..., alias="isCodaveri")
    live_feedback_enabled: bool = Field(..., alias="liveFeedbackEnabled")

# --- Models for TextResponse / FileUpload ---

class Attachment(BaseModel):
    id: str
    name: str

class TextResponseAnswer(AnswerBase):
    question_type: Literal["TextResponse"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    answer_text: str = Field(..., alias="answerText")
    attachments: list[Attachment] = Field(default_factory=list)
    explanation: Explanation
    latest_answer: "TextResponseAnswer | None" = Field(None, alias="latestAnswer")

class TextResponseQuestion(QuestionBase):
    type: Literal["TextResponse"]
    hide_text: bool = Field(..., alias="hideText")

class FileUploadAnswer(AnswerBase):
    question_type: Literal["FileUpload"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    attachments: list[Attachment] = Field(default_factory=list)
    explanation: Explanation
    latest_answer: "FileUploadAnswer | None" = Field(None, alias="latestAnswer")

class FileUploadQuestion(QuestionBase):
    type: Literal["FileUpload"]

# --- Models for Scribing ---

class Scribble(BaseModel):
    content: str
    creator_name: str
    creator_id: int

class ScribingAnswerData(BaseModel):
    image_url: str
    user_id: int
    answer_id: int
    scribbles: list[Scribble]

class ScribingAnswer(AnswerBase):
    question_type: Literal["Scribing"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    explanation: Explanation
    scribing_answer: ScribingAnswerData = Field(..., alias="scribing_answer")

class ScribingQuestion(QuestionBase):
    type: Literal["Scribing"]

# --- Models for VoiceResponse ---

class VoiceResponseFile(BaseModel):
    url: str | None = None
    name: str

class VoiceResponseAnswer(AnswerBase):
    question_type: Literal["VoiceResponse"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    file: VoiceResponseFile
    explanation: Explanation

class VoiceResponseQuestion(QuestionBase):
    type: Literal["VoiceResponse"]

# --- Models for ForumPostResponse ---

class ForumPostResponseAnswer(AnswerBase):
    question_type: Literal["ForumPostResponse"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    answer_text: str
    explanation: Explanation

class ForumPostResponseQuestion(QuestionBase):
    type: Literal["ForumPostResponse"]
    has_text_response: bool = Field(..., alias="hasTextResponse")

# --- Models for RubricBasedResponse ---

class RubricBasedResponseAnswer(AnswerBase):
    question_type: Literal["RubricBasedResponse"] = Field(..., alias="questionType")
    question: QuestionBase | None = None
    answer_text: str
    explanation: Explanation

class RubricBasedResponseQuestion(QuestionBase):
    type: Literal["RubricBasedResponse"]
    ai_grading_enabled: bool | None = Field(None, alias="aiGradingEnabled")

# --- Discriminated Unions ---

AnyAnswer = Annotated[
    Union[
        McqAnswer,
        ProgrammingAnswer,
        TextResponseAnswer,
        FileUploadAnswer,
        ScribingAnswer,
        VoiceResponseAnswer,
        ForumPostResponseAnswer,
        RubricBasedResponseAnswer,
    ],
    Field(discriminator='question_type')
]

AnyQuestion = Annotated[
    Union[
        McqQuestion,
        ProgrammingQuestion,
        TextResponseQuestion,
        FileUploadQuestion,
        ScribingQuestion,
        VoiceResponseQuestion,
        ForumPostResponseQuestion,
        RubricBasedResponseQuestion,
    ],
    Field(discriminator='type')
]

# --- The Final, Fully-Defined Model ---

class AnswerWithQuestion(BaseModel):
    answer: AnyAnswer
    question: AnyQuestion

# Rebuild models to resolve forward references for recursive fields like 'latest_answer'
McqAnswer.model_rebuild()
ProgrammingAnswer.model_rebuild()
TextResponseAnswer.model_rebuild()
FileUploadAnswer.model_rebuild()