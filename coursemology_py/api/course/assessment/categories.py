from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.assessment.categories import CategoriesIndexResponse


class CategoriesAPI(BaseCourseAPI):
    """
    API handler for fetching assessment categories and tabs.
    Mirrors `coursemology2/client/app/api/course/Assessment/Categories.js`.
    """

    @property
    def _url_prefix(self) -> str:
        # The URL is /courses/{id}/categories, not under /assessments
        return f"{super()._url_prefix}/categories"

    def index(self) -> CategoriesIndexResponse:
        """Fetches all assessment categories and their associated tabs."""
        return self._get("", response_model=CategoriesIndexResponse)
