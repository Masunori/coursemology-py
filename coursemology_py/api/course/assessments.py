from urllib.parse import urlparse

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.api.course.assessment.categories import CategoriesAPI
from coursemology_py.api.course.assessment.question import QuestionAPI
from coursemology_py.api.course.submission_questions import SubmissionQuestionsAPI
from coursemology_py.api.course.submissions import AssessmentSubmissionsAPI
from coursemology_py.auth import CoursemologySession
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.course.assessments import (
    AssessmentData,
    AssessmentEditData,
    AssessmentIDResponse,
    AssessmentPayload,
    AssessmentsIndexResponse,
    AssessmentUnlockRequirementsResponse,
    CreateAssessmentPayload,
    RedirectResponse,
    SkillsOptionsResponse,
)


class AssessmentsAPI(BaseCourseAPI):
    """
    API handler for assessments.
    Mirrors `coursemology2/client/app/api/course/Assessment/Assessments.js`.
    """

    def _get_relative_path(self, full_url: str) -> str:
        """Strips the host and /api/v1 prefix to get a relative path."""
        parsed_url = urlparse(full_url)
        api_prefix = urlparse(self._base_url).path
        if parsed_url.path.startswith(api_prefix):
            return parsed_url.path[len(api_prefix) :]
        return parsed_url.path

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/assessments"

    def index(self, category_id: int | None = None, tab_id: int | None = None) -> AssessmentsIndexResponse:
        params = {}
        if category_id:
            params["category"] = category_id
        if tab_id:
            params["tab"] = tab_id
        return self._get("", params=params, response_model=AssessmentsIndexResponse)

    def fetch(self, assessment_id: int) -> AssessmentData:
        return self._get(f"{assessment_id}", response_model=AssessmentData)

    def fetch_unlock_requirements(self, assessment_id: int) -> AssessmentUnlockRequirementsResponse:
        return self._get(
            f"{assessment_id}/requirements",
            response_model=AssessmentUnlockRequirementsResponse,
        )

    def fetch_edit_data(self, assessment_id: int) -> AssessmentEditData:
        return self._get(f"{assessment_id}/edit", response_model=AssessmentEditData)

    def create(self, payload: CreateAssessmentPayload) -> AssessmentIDResponse:
        return self._post("", json=payload.model_dump(by_alias=True, mode="json"), response_model=AssessmentIDResponse)

    def update(self, assessment_id: int, payload: AssessmentPayload) -> None:
        json_data = {"assessment": payload.model_dump(by_alias=True, mode="json")}
        self._patch(f"{assessment_id}", json=json_data, response_model=None)  # Server returns nothing

    def delete(self, delete_url: str) -> None:
        relative_path = self._get_relative_path(delete_url)
        self._delete(relative_path)

    def attempt(self, assessment_id: int) -> RedirectResponse:
        return self._get(f"{assessment_id}/attempt", response_model=RedirectResponse)

    def fetch_skills(self) -> SkillsOptionsResponse:
        return self._get("skills/options", response_model=SkillsOptionsResponse)

    def remind(self, assessment_id: int, course_users: list[int]) -> JobSubmitted:
        return self._post(
            f"{assessment_id}/remind",
            json={"course_users": course_users},
            response_model=JobSubmitted,
        )

    def reorder_questions(self, assessment_id: int, question_ids: list[int]) -> None:
        self._post(f"{assessment_id}/reorder", json={"question_order": question_ids})

    def duplicate_question(self, duplication_url: str) -> None:
        relative_path = self._get_relative_path(duplication_url)
        self._post(relative_path)

    def convert_mcq_mrq(self, convert_url: str) -> None:
        relative_path = self._get_relative_path(convert_url)
        self._patch(relative_path)

    def authenticate(self, assessment_id: int, password: str) -> RedirectResponse:
        return self._post(
            f"{assessment_id}/authenticate",
            json={"password": password},
            response_model=RedirectResponse,
        )


class AssessmentAPI:
    """A namespace class that groups all assessment-related API handlers."""

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int):
        # No more placeholders! Clean and correct.
        self.assessments = AssessmentsAPI(session, base_url, course_id)
        self.categories = CategoriesAPI(session, base_url, course_id)
        # We need a way to create the specific handlers like QuestionAPI
        self._session = session
        self._base_url = base_url
        self._course_id = course_id

    def question(self, assessment_id: int) -> QuestionAPI:
        """
        Returns an API handler for managing questions within a specific assessment.
        """
        return QuestionAPI(self._session, self._base_url, self._course_id, assessment_id)

    def submissions(self, assessment_id: int) -> AssessmentSubmissionsAPI:
        """
        Returns an API handler for managing submissions within a specific assessment.
        """
        return AssessmentSubmissionsAPI(self._session, self._base_url, self._course_id, assessment_id)

    def submission_questions(self, assessment_id: int) -> SubmissionQuestionsAPI:
        """
        Returns an API handler for submission questions within a specific assessment.

        Args:
            assessment_id: The ID of the assessment.

        Returns:
            An instance of SubmissionQuestionsAPI for that assessment.
        """
        return SubmissionQuestionsAPI(self._session, self._base_url, self._course_id, assessment_id)
