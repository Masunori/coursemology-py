from datetime import datetime

import polars as pl

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.auth import CoursemologySession
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.course.statistics import (
    AncestorAssessmentStats,
    AncestorInfo,
    AnswerDataWithQuestion,
    AssessmentLiveFeedbackStatistics,
    AssessmentsStatistics,
    CourseGetHelpActivity,
    CoursePerformanceStatistics,
    CourseProgressionStatistics,
    LearningRateRecordsData,
    LiveFeedbackHistoryState,
    MainAssessmentInfo,
    MainSubmissionInfo,
    StaffStatistics,
    StatisticsIndexData,
    StudentsStatistics,
)


class CourseStatisticsAPI(BaseCourseAPI):
    """
    API handler for course-level statistics.
    Mirrors `coursemology2/client/app/api/course/Statistics/CourseStatistics.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/statistics"

    def fetch_statistics_index(self) -> StatisticsIndexData:
        return self._get("", response_model=StatisticsIndexData)

    def fetch_all_student_statistics(self) -> StudentsStatistics:
        return self._get("students", response_model=StudentsStatistics)

    def fetch_all_student_statistics_df(self) -> pl.DataFrame:
        """
        Fetches statistics for all students and returns them as a Polars DataFrame.
        """
        stats = self.fetch_all_student_statistics()
        return pl.from_dicts([s.model_dump() for s in stats.students])

    def fetch_all_staff_statistics(self) -> StaffStatistics:
        return self._get("staff", response_model=StaffStatistics)

    def fetch_course_progression_statistics(self) -> CourseProgressionStatistics:
        return self._get("course/progression", response_model=CourseProgressionStatistics)

    def fetch_course_performance_statistics(self) -> CoursePerformanceStatistics:
        return self._get("course/performance", response_model=CoursePerformanceStatistics)

    def fetch_assessments_statistics(self) -> AssessmentsStatistics:
        return self._get("assessments", response_model=AssessmentsStatistics)

    def fetch_course_get_help_activity(
        self, start_at: datetime | None = None, end_at: datetime | None = None
    ) -> list[CourseGetHelpActivity]:
        params = {}
        if start_at:
            params["start_at"] = start_at.isoformat()
        if end_at:
            params["end_at"] = end_at.isoformat()

        return self._get(
            "get_help",
            response_model=list[CourseGetHelpActivity],
            params=params if params else None,
        )

    def download_score_summary(self, assessment_ids: list[int]) -> JobSubmitted:
        return self._get(
            "assessments/download",
            response_model=JobSubmitted,
            params={"assessment_ids": assessment_ids},
        )


class UserStatisticsAPI(BaseCourseAPI):
    """
    API handler for individual user-level statistics.
    Mirrors `UserStatistics.ts`.
    """

    def __init__(
        self,
        session: CoursemologySession,
        base_url: str,
        course_id: int,
        course_user_id: int,
    ):
        super().__init__(session, base_url, course_id)
        self._course_user_id = course_user_id

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/statistics/user/{self._course_user_id}"

    def fetch_learning_rate_records(self) -> LearningRateRecordsData:
        """Fetches the history of learning rate records for the user."""
        return self._get("learning_rate_records", response_model=LearningRateRecordsData)


class AnswerStatisticsAPI(BaseCourseAPI):
    """
    API handler for answer-level statistics.
    Mirrors `AnswerStatistics.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/statistics/answers"

    def fetch(self, answer_id: int) -> AnswerDataWithQuestion:
        """Fetches a specific answer's statistics."""
        return self._get(f"{answer_id}", response_model=AnswerDataWithQuestion)


class AssessmentStatisticsAPI(BaseCourseAPI):
    """
    API handler for individual assessment-level statistics.
    Mirrors `AssessmentStatistics.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/statistics/assessment"

    def fetch_ancestor_statistics(self, ancestor_id: int) -> AncestorAssessmentStats:
        return self._get(f"{ancestor_id}/ancestor_statistics", response_model=AncestorAssessmentStats)

    def fetch_assessment_statistics(self, assessment_id: int) -> MainAssessmentInfo | None:
        return self._get(f"{assessment_id}/assessment_statistics", response_model=MainAssessmentInfo)

    def fetch_submission_statistics(self, assessment_id: int) -> list[MainSubmissionInfo]:
        return self._get(
            f"{assessment_id}/submission_statistics",
            response_model=list[MainSubmissionInfo],
        )

    def fetch_live_feedback_statistics(self, assessment_id: int) -> list[AssessmentLiveFeedbackStatistics]:
        return self._get(
            f"{assessment_id}/live_feedback_statistics",
            response_model=list[AssessmentLiveFeedbackStatistics],
        )

    def fetch_live_feedback_history(
        self, assessment_id: int, question_id: int, course_user_id: int
    ) -> LiveFeedbackHistoryState:
        params = {"question_id": question_id, "course_user_id": course_user_id}
        return self._get(
            f"{assessment_id}/live_feedback_history",
            params=params,
            response_model=LiveFeedbackHistoryState,
        )

    def fetch_ancestor_info(self, assessment_id: int) -> list[AncestorInfo]:
        return self._get(f"{assessment_id}/ancestor_info", response_model=list[AncestorInfo])


class StatisticsAPI:
    """
    A namespace class that groups all statistics-related API handlers.
    """

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int):
        self._session = session
        self._base_url = base_url
        self._course_id = course_id
        self.course = CourseStatisticsAPI(session, base_url, course_id)
        self.assessment = AssessmentStatisticsAPI(session, base_url, course_id)
        self.answer = AnswerStatisticsAPI(session, base_url, course_id)

    def user(self, course_user_id: int) -> UserStatisticsAPI:
        """
        Returns an API handler for a specific user's statistics.

        Args:
            course_user_id: The ID of the course user.

        Returns:
            An instance of UserStatisticsAPI configured for the specified user.
        """
        return UserStatisticsAPI(self._session, self._base_url, self._course_id, course_user_id)
