from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.groups import (
    CreateGroupsResponse,
    GroupCategoriesIndexResponse,
    GroupCategoryInfoResponse,
    GroupCategoryPayload,
    GroupCourseUsersResponse,
    GroupPayload,
    SimpleIdResponse,
    UpdateGroupMembersPayload,
    UpdateGroupResponse,
)


class GroupsAPI(BaseCourseAPI):
    """
    API handler for course groups and categories.
    Mirrors `coursemology2/client/app/api/course/Groups.js`.
    """

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/groups"

    def fetch_group_categories(self) -> GroupCategoriesIndexResponse:
        """Fetches a list of all group categories in the course."""
        return self._get("", response_model=GroupCategoriesIndexResponse)

    def fetch(self, group_category_id: int) -> GroupCategoryInfoResponse:
        """Fetches a single category and its groups and members."""
        return self._get(f"{group_category_id}/info", response_model=GroupCategoryInfoResponse)

    def fetch_course_users(self, group_category_id: int) -> GroupCourseUsersResponse:
        """Fetches a list of course users available for assignment to a group."""
        return self._get(f"{group_category_id}/users", response_model=GroupCourseUsersResponse)

    def create_category(self, payload: GroupCategoryPayload) -> SimpleIdResponse:
        """Creates a new group category."""
        request_body = payload.model_dump(exclude_none=True)
        return self._post("", json=request_body, response_model=SimpleIdResponse)

    def create_groups(self, category_id: int, payload: list[GroupPayload]) -> CreateGroupsResponse:
        """Creates one or more groups under a specified category."""
        request_body = {"groups": [p.model_dump(exclude_none=True) for p in payload]}
        return self._post(f"{category_id}/groups", json=request_body, response_model=CreateGroupsResponse)

    def update_category(self, category_id: int, payload: GroupCategoryPayload) -> SimpleIdResponse:
        """Updates a group category."""
        request_body = payload.model_dump(exclude_none=True)
        return self._patch(f"{category_id}", json=request_body, response_model=SimpleIdResponse)

    def update_group(self, category_id: int, group_id: int, payload: GroupPayload) -> UpdateGroupResponse:
        """Updates a single group."""
        request_body = payload.model_dump(exclude_none=True)
        return self._patch(
            f"{category_id}/groups/{group_id}",
            json=request_body,
            response_model=UpdateGroupResponse,
        )

    def update_group_members(self, category_id: int, payload: UpdateGroupMembersPayload) -> SimpleIdResponse:
        """Updates the members of one or more groups within a category."""
        return self._patch(
            f"{category_id}/group_members",
            json=payload.model_dump(),
            response_model=SimpleIdResponse,
        )

    def delete_group(self, category_id: int, group_id: int) -> SimpleIdResponse:
        """Deletes a single group."""
        return self._delete(f"{category_id}/groups/{group_id}", response_model=SimpleIdResponse)

    def delete_category(self, category_id: int) -> SimpleIdResponse:
        """Deletes a group category."""
        return self._delete(f"{category_id}", response_model=SimpleIdResponse)
