from datetime import datetime

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.disbursement import (
    DisbursementCreateResponse,
    DisbursementIndexResponse,
    DisbursementPayload,
    ForumDisbursementIndexResponse,
    ForumDisbursementPayload,
)
from coursemology_py.utils import build_form_data


class DisbursementAPI(BaseCourseAPI):
    """
    API handler for disbursing experience points to users.
    Mirrors `coursemology2/client/app/api/course/Disbursement.ts`.
    """

    @property
    def _std_url_prefix(self) -> str:
        return "users/disburse_experience_points"

    @property
    def _forum_url_prefix(self) -> str:
        return "users/forum_disbursement"

    def index(self) -> DisbursementIndexResponse:
        """Fetches initial data for standard EXP disbursement."""
        return self._get(self._std_url_prefix, response_model=DisbursementIndexResponse)

    def create(self, payload: DisbursementPayload) -> DisbursementCreateResponse:
        """Creates a new standard experience points disbursement."""
        form_data = build_form_data(payload, "experience_points_disbursement")
        return self._post(self._std_url_prefix, data=form_data, response_model=DisbursementCreateResponse)

    def forum_disbursement_index(
        self, start_time: datetime, end_time: datetime, weekly_cap: int
    ) -> ForumDisbursementIndexResponse:
        """Fetches data for forum EXP disbursement based on filters."""
        params: dict[str, str | int] = {
            "experience_points_forum_disbursement[start_time]": start_time.isoformat(),
            "experience_points_forum_disbursement[end_time]": end_time.isoformat(),
            "experience_points_forum_disbursement[weekly_cap]": weekly_cap,
        }
        return self._get(self._forum_url_prefix, params=params, response_model=ForumDisbursementIndexResponse)

    def forum_disbursement_create(self, payload: ForumDisbursementPayload) -> DisbursementCreateResponse:
        """Creates a new forum experience points disbursement."""
        form_data = build_form_data(payload, "experience_points_disbursement")
        return self._post(self._forum_url_prefix, data=form_data, response_model=DisbursementCreateResponse)
