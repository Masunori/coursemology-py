import uuid

from coursemology_py.api.course import CourseAPI
from coursemology_py.models.course.user_invitations import UserInvitation
from coursemology_py.models.course.users import (
    CourseUser,
    CourseUserBasic,
    CourseUserBasicMini,
    StudentsIndexResponse,
    UpdateCourseUser,
    UserFetchResponse,
    UsersIndexBasicResponse,
    UsersIndexResponse,
)

# --- Read-Only Tests ---


def test_users_index_students(course_api: CourseAPI) -> None:
    """Tests fetching the list of all students in the course."""
    response = course_api.users.index_students()
    assert isinstance(response, StudentsIndexResponse)
    assert isinstance(response.users, list)
    if response.users:
        assert isinstance(response.users[0], CourseUser)
        assert response.users[0].role == "student"


def test_users_index_staff(course_api: CourseAPI) -> None:
    """Tests fetching the list of all staff in the course."""
    response = course_api.users.index_staff()
    assert isinstance(response, UsersIndexResponse)
    assert isinstance(response.users, list)
    if response.users:
        assert isinstance(response.users[0], CourseUser)
        assert response.users[0].role in ["manager", "owner", "teaching_assistant", "observer"]


def test_users_index_basic_and_detailed(course_api: CourseAPI) -> None:
    """Tests the index endpoint with both as_basic_data flags."""
    basic_response = course_api.users.index(as_basic_data=True)
    assert isinstance(basic_response, UsersIndexBasicResponse)
    assert isinstance(basic_response.users, list)
    if basic_response.users:
        assert isinstance(basic_response.users[0], CourseUserBasic)

    detailed_response = course_api.users.index(as_basic_data=False)
    assert isinstance(detailed_response, UsersIndexResponse)
    assert isinstance(detailed_response.users, list)
    if detailed_response.users:
        assert isinstance(detailed_response.users[0], CourseUser)


def test_users_fetch(course_api: CourseAPI, test_user: CourseUser) -> None:
    """Tests fetching a single, specific user by ID."""
    response = course_api.users.fetch(test_user.id)
    assert isinstance(response, UserFetchResponse)
    fetched_user = response.user
    assert fetched_user.id == test_user.id
    assert fetched_user.name == test_user.name


# --- Write, Update, and Invitation Tests ---


def test_user_invitations_invite_new_user(pending_invitation: UserInvitation) -> None:
    """
    Tests that a pending invitation was created successfully.
    The setup and cleanup are handled entirely by the 'pending_invitation' fixture.
    """
    assert isinstance(pending_invitation, UserInvitation)
    assert isinstance(pending_invitation.id, int)
    assert "@example.com" in pending_invitation.email


def test_user_update(course_api: CourseAPI, test_user: CourseUser) -> None:
    """Tests updating an active user's name."""
    new_name = f"Updated Name {uuid.uuid4().hex[:8]}"
    payload = UpdateCourseUser(name=new_name)
    response = course_api.users.update(test_user.id, payload)
    assert response.name == new_name


def test_user_upgrade_to_staff(course_api: CourseAPI, test_user: CourseUser) -> None:
    """Tests upgrading an active student to a teaching assistant and reverting."""
    user_to_upgrade = CourseUserBasicMini(id=test_user.id, name=test_user.name)
    try:
        course_api.users.upgrade_to_staff(users=[user_to_upgrade], role="teaching_assistant")
        fetched_user = course_api.users.fetch(test_user.id).user
        assert fetched_user.role == "teaching_assistant"
    finally:
        # Revert the change to leave the session-wide user in a clean state
        revert_payload = UpdateCourseUser(role="student")
        course_api.users.update(test_user.id, revert_payload)
