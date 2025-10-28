from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.course.experience_points import (
    ExperiencePointsRecord,
    ExperiencePointsRecordPayload,
    ExperiencePointsRecordsForUserResponse,
    ExperiencePointsRecordsResponse,
)


class ExperiencePointsRecordAPI(BaseCourseAPI):
    """
    API handler for course experience points records.
    """

    @property
    def _url_prefix(self) -> str:
        return super()._url_prefix

    def fetch_all_exp(self, page_num: int, student_id: int | None = None) -> ExperiencePointsRecordsResponse:
        """
        Fetches all experience points records for all users in the course.
        """
        params = {"filter[page_num]": page_num}
        if student_id:
            params["filter[student_id]"] = student_id

        return self._get(
            "experience_points_records",
            params=params,
            response_model=ExperiencePointsRecordsResponse,
        )

    def download_csv(self, student_id: int | None = None) -> JobSubmitted:
        """
        Triggers a background job to download EXP records as a CSV.
        """
        params = {}
        if student_id:
            params["filter[student_id]"] = student_id

        return self._get(
            "experience_points_records/download",
            params=params if params else None,
            response_model=JobSubmitted,
        )

    def fetch_exp_for_user(self, user_id: int, page_num: int = 1) -> ExperiencePointsRecordsForUserResponse:
        """
        Fetches all experience points records for a specific user.
        """
        return self._get(
            f"users/{user_id}/experience_points_records",
            params={"filter[page_num]": page_num},
            response_model=ExperiencePointsRecordsForUserResponse,
        )

    def update(self, record_id: int, student_id: int, payload: ExperiencePointsRecordPayload) -> ExperiencePointsRecord:
        """
        Updates an experience points record for a user.
        """
        request_body = {"experience_points_record": payload.model_dump(by_alias=True)}
        return self._patch(
            f"users/{student_id}/experience_points_records/{record_id}",
            json=request_body,
            response_model=ExperiencePointsRecord,
        )

    def delete(self, record_id: int, student_id: int) -> None:
        """
        Deletes an experience points record for a user.
        """
        self._delete(f"users/{student_id}/experience_points_records/{record_id}")
