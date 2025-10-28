from typing import Any

from coursemology_py.api.assessment_base import BaseAssessmentAPI
from coursemology_py.auth import CoursemologySession
from coursemology_py.models.course.assessment.questions import (
    CodaveriGenerateResponse,
    JustRedirect,
    Language,
    McqMrqFormData,
    McqMrqPostData,
    PackageImportResultData,
    ProgrammingFormData,
    ProgrammingPostStatusData,
    ProgrammingQuestion,
    RedirectWithEditUrl,
    TextResponseFormData,
    TextResponseQuestion,
    UpdateQnSettingPayload,
)
# Import the new utility
from coursemology_py.utils import build_form_data


class McqMrqAPI(BaseAssessmentAPI):
    """API handler for Multiple Choice and Multiple Response questions."""

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/question/multiple_responses"

    def fetch_new_mrq(self) -> McqMrqFormData:
        return self._get("new", response_model=McqMrqFormData)

    def fetch_new_mcq(self) -> McqMrqFormData:
        return self._get("new", params={"multiple_choice": True}, response_model=McqMrqFormData)

    def fetch_edit(self, question_id: int) -> McqMrqFormData:
        return self._get(f"{question_id}/edit", response_model=McqMrqFormData)

    def create(self, payload: McqMrqPostData) -> RedirectWithEditUrl:
        return self._post("", json=payload.model_dump(by_alias=True), response_model=RedirectWithEditUrl)

    def update(self, question_id: int, payload: McqMrqPostData) -> RedirectWithEditUrl:
        return self._patch(f"{question_id}", json=payload.model_dump(by_alias=True), response_model=RedirectWithEditUrl)


class TextResponseAPI(BaseAssessmentAPI):
    """API handler for Text Response and File Upload questions."""

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/question/text_responses"

    def fetch_new_text_response(self) -> TextResponseFormData:
        return self._get("new", response_model=TextResponseFormData)

    def fetch_new_file_upload(self) -> TextResponseFormData:
        return self._get("new", params={"file_upload": True}, response_model=TextResponseFormData)

    def fetch_edit(self, question_id: int) -> TextResponseFormData:
        return self._get(f"{question_id}/edit", response_model=TextResponseFormData)

    def create(self, payload: TextResponseQuestion) -> JustRedirect:
        form_data = build_form_data(payload, "question_text_response")
        return self._post("", data=form_data, response_model=JustRedirect)

    def update(self, question_id: int, payload: TextResponseQuestion) -> JustRedirect:
        form_data = build_form_data(payload, "question_text_response")
        return self._patch(f"{question_id}", data=form_data, response_model=JustRedirect)


class ProgrammingAPI(BaseAssessmentAPI):
    """API handler for Programming questions."""

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/question/programming"

    def fetch_new(self) -> ProgrammingFormData:
        return self._get("new", response_model=ProgrammingFormData)

    def fetch_edit(self, question_id: int) -> ProgrammingFormData:
        return self._get(f"{question_id}/edit", response_model=ProgrammingFormData)

    def fetch_import_result(self, question_id: int) -> PackageImportResultData:
        return self._get(f"{question_id}/import_result", response_model=PackageImportResultData)

    def create(self, payload: ProgrammingQuestion) -> ProgrammingPostStatusData:
        form_data = build_form_data(payload, "question_programming")
        return self._post("", data=form_data, response_model=ProgrammingPostStatusData)

    def update(self, question_id: int, payload: ProgrammingQuestion) -> ProgrammingPostStatusData:
        form_data = build_form_data(payload, "question_programming")
        return self._patch(f"{question_id}", data=form_data, response_model=ProgrammingPostStatusData)

    def fetch_codaveri_languages(self) -> list[Language]:
        return self._get("codaveri_languages", response_model=list[Language])

    def generate(self, form_data: dict[str, Any]) -> CodaveriGenerateResponse:
        # This endpoint expects FormData, so we pass the dict directly
        return self._post("generate", data=form_data, response_model=CodaveriGenerateResponse)

    def update_qn_setting(self, question_id: int, payload: UpdateQnSettingPayload) -> None:
        self._patch(f"{question_id}/update_question_setting", json=payload.model_dump(by_alias=True))


class QuestionAPI:
    """A namespace class that groups all question-type-specific API handlers."""

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int, assessment_id: int):
        self.mcq_mrq = McqMrqAPI(session, base_url, course_id, assessment_id)
        self.text_response = TextResponseAPI(session, base_url, course_id, assessment_id)
        self.programming = ProgrammingAPI(session, base_url, course_id, assessment_id)