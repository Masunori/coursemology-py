from typing import Literal, overload

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.users import (
    CourseUser,
    CourseUserBasicMini,
    StaffRoles,
    StudentsIndexResponse,
    UpdateCourseUser,
    UserFetchResponse,
    UsersIndexBasicResponse,
    UsersIndexResponse,
)


class UsersAPI(BaseCourseAPI):
    """
    API handler for course users.
    Mirrors `coursemology_py/client/app/api/course/Users.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        # The base for this API is just the course, not a sub-path
        return super()._url_prefix

    @overload
    def index(self, *, as_basic_data: Literal[True]) -> UsersIndexBasicResponse: ...

    @overload
    def index(self, *, as_basic_data: Literal[False] = False) -> UsersIndexResponse: ...

    def index(self, *, as_basic_data: bool = False) -> UsersIndexResponse | UsersIndexBasicResponse:
        """
        Fetches a list of users in a course.

        Args:
            as_basic_data: If True, returns a basic list of users.
                           If False (default), returns a detailed list of students.

        Returns:
            A response object containing the list of users and related metadata.
        """
        response_model = UsersIndexBasicResponse if as_basic_data else UsersIndexResponse
        return self._get(
            "users",
            response_model=response_model,
            params={"as_basic_data": as_basic_data},
        )

    def index_students(self) -> StudentsIndexResponse:
        """Fetches a list of all students in the course."""
        return self._get("students", response_model=StudentsIndexResponse)

    def index_staff(self) -> UsersIndexResponse:
        """Fetches a list of all staff members in the course."""
        return self._get("staff", response_model=UsersIndexResponse)

    def fetch(self, user_id: int) -> UserFetchResponse:
        """Fetches detailed information for a single course user."""
        return self._get(f"users/{user_id}", response_model=UserFetchResponse)

    def delete(self, user_id: int) -> None:
        """Deletes a user from the course."""
        self._delete(f"users/{user_id}")

    def update(self, user_id: int, params: UpdateCourseUser) -> CourseUser:
        """
        Updates a course user's details.

        Args:
            user_id: The ID of the user to update.
            params: A Pydantic model containing the fields to update.
        """
        payload = {"course_user": params.model_dump(exclude_unset=True)}
        return self._patch(f"users/{user_id}", json=payload, response_model=CourseUser)

    def upgrade_to_staff(self, users: list[CourseUserBasicMini], role: StaffRoles) -> None:
        """
        Upgrades a list of students to a staff role.

        Args:
            users: A list of user objects (must contain at least 'id').
            role: The target staff role.
        """
        user_ids = [user.id for user in users]
        payload: dict[str, dict[str, list[int] | StaffRoles | int]] = {
            "course_users": {"ids": user_ids, "role": role},
            "user": {"id": user_ids[0]},
        }
        print(payload)
        self._patch("upgrade_to_staff", json=payload)
