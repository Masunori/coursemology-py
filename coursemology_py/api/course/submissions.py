from typing import Any, cast

import requests

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.api.course.answers import AnswerAPI
from coursemology_py.auth import CoursemologySession
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.course.assessment.answer_with_question import AnyAnswer
from coursemology_py.models.course.submissions import (
    AssessmentSubmissionsIndexResponse,
    LiveFeedbackChat,
    LiveFeedbackThread,
    ProgrammingAnnotationPayload,
    ReloadAnswerResponse,
    SubmissionEditData,
    SubmissionGradeUpdate,
    TopLevelSubmissionsIndexResponse,
)
from coursemology_py.utils import build_form_data


class TopLevelSubmissionsAPI(BaseCourseAPI):
    """
    API handler for viewing submissions across all assessments.
    Mirrors `Submissions/Submissions.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/assessments/submissions"

    def index(self) -> TopLevelSubmissionsIndexResponse:
        return self._get("", response_model=TopLevelSubmissionsIndexResponse)

    def pending(self, my_students: bool) -> TopLevelSubmissionsIndexResponse:
        return self._get(
            "pending",
            params={"my_students": my_students},
            response_model=TopLevelSubmissionsIndexResponse,
        )

    def category(self, category_id: int) -> TopLevelSubmissionsIndexResponse:
        return self._get(
            "",
            params={"category": category_id},
            response_model=TopLevelSubmissionsIndexResponse,
        )

    def filter(
        self,
        category_id: int | None = None,
        assessment_id: int | None = None,
        group_id: int | None = None,
        user_id: int | None = None,
        page_num: int | None = None,
    ) -> TopLevelSubmissionsIndexResponse:
        params = {
            "filter[category_id]": category_id,
            "filter[assessment_id]": assessment_id,
            "filter[group_id]": group_id,
            "filter[user_id]": user_id,
            "filter[page_num]": page_num,
        }
        cleaned_params = {k: v for k, v in params.items() if v is not None}
        return self._get("", params=cleaned_params, response_model=TopLevelSubmissionsIndexResponse)

    def filter_pending(
        self,
        my_students: bool,
        page_num: int | None = None,
    ) -> TopLevelSubmissionsIndexResponse:
        """Filters pending submissions, used for pagination."""
        return self._get(
            f"pending?my_students={my_students}",
            params={"filter[page_num]": page_num} if page_num else None,
            response_model=TopLevelSubmissionsIndexResponse,
        )


class AssessmentSubmissionsAPI(BaseCourseAPI):
    """
    API handler for managing submissions within a single assessment.
    Mirrors `Assessment/Submissions.js`.
    """

    def __init__(
        self,
        session: CoursemologySession,
        base_url: str,
        course_id: int,
        assessment_id: int,
    ):
        super().__init__(session, base_url, course_id)
        self._assessment_id = assessment_id

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/assessments/{self._assessment_id}/submissions"

    def index(self) -> AssessmentSubmissionsIndexResponse:
        return self._get("", response_model=AssessmentSubmissionsIndexResponse)

    def download_all(self, course_users: list[int], download_format: str) -> JobSubmitted:
        params: dict[str, list[int] | str] = {
            "course_users": course_users,
            "download_format": download_format,
        }
        return self._get("download_all", params=params, response_model=JobSubmitted)

    def publish_all(self, course_users: list[int]) -> JobSubmitted:
        return self._patch("publish_all", json={"course_users": course_users}, response_model=JobSubmitted)

    def force_submit_all(self, course_users: list[int]) -> JobSubmitted:
        return self._patch("force_submit_all", json={"course_users": course_users}, response_model=JobSubmitted)

    def finalize(self, submission_id: int) -> None:
        payload = {
            "submission": {
                "finalise": True
            }
        }
        self._patch(f"{submission_id}", json=payload)

    def unsubmit(self, submission_id: int) -> None:
        self._patch(f"{submission_id}/unsubmit")

    def unsubmit_all(self, course_users: list[int]) -> JobSubmitted:
        return self._patch("unsubmit_all", json={"course_users": course_users}, response_model=JobSubmitted)

    def delete(self, submission_id: int) -> None:
        self._delete(f"{submission_id}")

    def delete_all(self, course_users: list[int]) -> JobSubmitted:
        return self._patch("delete_all", json={"course_users": course_users}, response_model=JobSubmitted)

    def edit(self, submission_id: int) -> SubmissionEditData:
        return self._get(f"{submission_id}/edit", response_model=SubmissionEditData)

    def update_grade(self, submission_id: int, grades: SubmissionGradeUpdate) -> None:
        """Updates grades for answers in a submission."""
        payload = {"submission": grades.model_dump()}
        self._patch(f"{submission_id}", json=payload)

    def update(self, submission_id: int, submission_fields: dict[str, Any]) -> None:
        # Here, the root key is 'submission' by default in the reference client.
        form_data = build_form_data(submission_fields, "submission")
        self._patch(f"{submission_id}", data=form_data)

    def reload_answer(self, submission_id: int, answer_id: int) -> ReloadAnswerResponse:
        return self._post(
            f"{submission_id}/reload_answer",
            json={"answer_id": answer_id},
            response_model=ReloadAnswerResponse,
        )

    def auto_grade(self, submission_id: int) -> JobSubmitted:
        return self._post(f"{submission_id}/auto_grade", response_model=JobSubmitted)

    def reevaluate_answer(self, submission_id: int, answer_id: int) -> JobSubmitted:
        return self._post(
            f"{submission_id}/reevaluate_answer",
            json={"answer_id": answer_id},
            response_model=JobSubmitted,
        )

    def generate_feedback(self, submission_id: int, answer_id: int) -> JobSubmitted:
        return self._post(
            f"{submission_id}/generate_feedback",
            json={"answer_id": answer_id},
            response_model=JobSubmitted,
        )

    def generate_live_feedback(
        self,
        submission_id: int,
        answer_id: int,
        thread_id: str,
        message: str,
        options: list[str] | None = None,
        option_id: int | None = None,
    ) -> LiveFeedbackThread:
        payload: dict[str, int | str | list[str] | None] = {
            "answer_id": answer_id,
            "thread_id": thread_id,
            "message": message,
            "options": options,
            "option_id": option_id,
        }
        cleaned_payload = {k: v for k, v in payload.items() if v is not None}
        return self._post(
            f"{submission_id}/generate_live_feedback",
            json=cleaned_payload,
            response_model=LiveFeedbackThread,
        )

    def fetch_live_feedback(self, feedback_url: str, feedback_token: str) -> Any:
        with requests.Session() as external_session:
            response = external_session.get(
                f"{feedback_url}/signed/chat/feedback/messages",
                headers={"x-api-version": "2.1"},
                params={"token": feedback_token},
            )
            response.raise_for_status()
            return response.json()

    def fetch_live_feedback_chat(self, answer_id: int) -> LiveFeedbackChat:
        return self._get(
            "fetch_live_feedback_chat",
            params={"answer_id": answer_id},
            response_model=LiveFeedbackChat,
        )

    def create_live_feedback_chat(self, submission_id: int, params: dict[str, int]) -> LiveFeedbackChat:
        """Creates a live feedback chat session."""
        return self._post(
            f"{submission_id}/create_live_feedback_chat",
            json=params,
            response_model=LiveFeedbackChat,
        )

    def fetch_live_feedback_status(self, thread_id: str) -> dict[str, str]:
        """Fetches the status of a live feedback thread."""
        return self._get(
            "fetch_live_feedback_status",
            params={"thread_id": thread_id},
            response_model=dict[str, str],
        )

    def save_live_feedback(self, current_thread_id: str, content: str, is_error: bool) -> None:
        """Saves live feedback content."""
        payload = {
            "current_thread_id": current_thread_id,
            "content": content,
            "is_error": is_error,
        }
        self._post("save_live_feedback", json=payload)

    def fetch_answer(self, submission_id: int, answer_id: int) -> AnyAnswer:
        """
        Fetches an answer with a given id.
        This corresponds to the fetchAnswer method in TypeScript.
        """
        result = self._get(f"{submission_id}/answers/{answer_id}", response_model=AnyAnswer)  # type: ignore
        return cast(AnyAnswer, result)

    def create_programming_annotation(
        self,
        submission_id: int,
        answer_id: int,
        file_id: int,
        payload: ProgrammingAnnotationPayload,
    ) -> None:
        url = f"{submission_id}/answers/{answer_id}/programming/files/{file_id}/annotations"
        self._post(url, json=payload.model_dump())

    def answer(self, submission_id: int) -> AnswerAPI:
        """
        Returns an API handler for managing answers within a specific submission.

        Args:
            submission_id: The ID of the submission.

        Returns:
            An instance of AnswerAPI for that submission.
        """
        return AnswerAPI(self._session, self._base_url, self._course_id, self._assessment_id, submission_id)

    def download_statistics(self, course_users: list[int]) -> JobSubmitted:
        """Starts a background job to download submission statistics."""
        params = {"course_users": course_users}
        return self._get("download_statistics", params=params, response_model=JobSubmitted)

    def fetch_submissions_from_koditsu(self) -> None:
        """Triggers a fetch of submissions from the Koditsu service."""
        self._patch("fetch_submissions_from_koditsu")