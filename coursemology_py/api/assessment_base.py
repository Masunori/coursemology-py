from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.auth import CoursemologySession


class BaseAssessmentAPI(BaseCourseAPI):
    """
    A specialized base class for APIs that operate within the context of a
    specific assessment. It requires an assessment_id to be initialized.
    """

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int, assessment_id: int):
        super().__init__(session, base_url, course_id)
        self._assessment_id = assessment_id

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/assessments/{self._assessment_id}"
