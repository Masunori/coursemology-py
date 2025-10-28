from coursemology_py.api.assessment_base import BaseAssessmentAPI
from coursemology_py.auth import CoursemologySession
from coursemology_py.models.course.submission_questions import (
    CommentPayload,
    SubmissionQuestionComment,
    SubmissionQuestionDetails,
)


class SubmissionQuestionsAPI(BaseAssessmentAPI):
    """
    API handler for submission questions within a specific assessment.
    Mirrors `SubmissionQuestions.js` and parts of `AllAnswers.ts`.
    """

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int, assessment_id: int):
        super().__init__(session, base_url, course_id, assessment_id)

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/assessments/{self._assessment_id}"

    def create_comment(self, submission_question_id: int, payload: CommentPayload) -> SubmissionQuestionComment:
        """
        Creates a comment on a specific submission question.
        """
        request_body = {"discussion_post": payload.model_dump()}
        url_path = f"submission_questions/{submission_question_id}/comments"
        return self._post(url_path, json=request_body, response_model=SubmissionQuestionComment)

    def fetch_details(self, submission_id: int, question_id: int) -> SubmissionQuestionDetails:
        """
        Fetches all past answers and comments for a given question.
        This corresponds to the `fetchSubmissionQuestionDetails` method.

        Args:
            submission_id: The ID of the submission context.
            question_id: The ID of the question to fetch details for.
        """
        url_path = f"submissions/{submission_id}/questions/{question_id}/all_answers"
        return self._get(url_path, response_model=SubmissionQuestionDetails)
