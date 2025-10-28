from typing import cast, Union

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.auth import CoursemologySession
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.course.assessment.answer_payloads import (
    ProgrammingAnswerPayload,
    McqMrqAnswerPayload,
    TextResponseAnswerPayload,
    VoiceResponseAnswerPayload,
    ForumPostResponseAnswerPayload,
    RubricBasedResponseAnswerPayload,
    ScribingAnswerPayload,
    FileUploadAnswerPayload,
)
from coursemology_py.models.course.assessment.answer_with_question import AnyAnswer

# Union type for all answer payloads
AnyAnswerPayload = Union[
    ProgrammingAnswerPayload,
    McqMrqAnswerPayload,
    TextResponseAnswerPayload,
    VoiceResponseAnswerPayload,
    ForumPostResponseAnswerPayload,
    RubricBasedResponseAnswerPayload,
    ScribingAnswerPayload,
    FileUploadAnswerPayload,
]


class AnswerAPI(BaseCourseAPI):
    """
    API handler for saving and submitting individual answers within a submission.
    """

    def __init__(
        self, session: CoursemologySession, base_url: str, course_id: int, assessment_id: int, submission_id: int
    ):
        super().__init__(session, base_url, course_id)
        self._assessment_id = assessment_id
        self._submission_id = submission_id

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/assessments/{self._assessment_id}/submissions/{self._submission_id}/answers"

    def save_draft(self, payload: AnyAnswerPayload) -> AnyAnswer:
        """
        Saves the current state of an answer as a draft.
        """
        request_body = {"answer": payload.model_dump(exclude_none=True)}

        # The call to _patch with a UnionType response_model confuses mypy's overload resolution.
        # We call the method, which works at runtime, and then cast the result to the
        # correct type to satisfy the static type checker.
        result = self._patch(f"{payload.id}", json=request_body, response_model=AnyAnswer)  # type: ignore
        return cast(AnyAnswer, result)

    def submit_answer(self, payload: AnyAnswerPayload) -> JobSubmitted:
        """
        Submits an answer for autograding.
        """
        request_body = {"answer": payload.model_dump(exclude_none=True)}
        return self._patch(f"{payload.id}/submit_answer", json=request_body, response_model=JobSubmitted)

    def fetch(self, answer_id: int) -> AnyAnswer:
        """
        Fetches a single answer with its associated question details.
        """
        # Apply the same cast pattern here for the same reason.
        result = self._get(f"{answer_id}", response_model=AnyAnswer)  # type: ignore
        return cast(AnyAnswer, result)