import os
import uuid
from collections.abc import Generator
from dotenv import load_dotenv

import pytest
from coursemology_py import CoursemologyClient
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.course.assessment.categories import TabBasic
from coursemology_py.models.course.user_invitations import (
    IndividualInvite,
    InvitationsFormPayload,
    UserInvitation,
)
from coursemology_py.models.course.users import CourseUser

# --- Test Configuration ---
load_dotenv()
HOST = "https://coursemology.org"
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
COURSE_ID = os.environ.get("COURSE_ID")
TEST_USERNAME = os.environ.get("TEST_USERNAME")


@pytest.fixture(scope="session")
def authenticated_client() -> Generator[CoursemologyClient]:
    """Logs into Coursemology once per test session."""
    print(f"\nAttempting to log in to {HOST} as user '{USERNAME}'...")
    client = CoursemologyClient(host=HOST)
    try:
        client.login(username=USERNAME, password=PASSWORD)
        print("Login successful. Yielding authenticated client to tests.")
        yield client
    except CoursemologyAPIError as e:
        pytest.fail(f"Failed to authenticate for integration tests: {e}")


@pytest.fixture(scope="session")
def course_api(authenticated_client: CoursemologyClient) -> CourseAPI:
    """Provides a CourseAPI instance for a specific course, once per session."""
    print(f"Creating CourseAPI handler for course_id={COURSE_ID}...")
    return authenticated_client.course(course_id=COURSE_ID)


@pytest.fixture(scope="session")
def test_user(course_api: CourseAPI) -> Generator[CourseUser]:
    """
    Creates a temporary but active user in the course once per session by inviting
    an existing Coursemology user ('test@test.com').

    This user can be used across all test files for operations requiring an active user.
    Cleans up by deleting the user at the end of the entire test session.
    """
    user_email = TEST_USERNAME
    user_name = f"Test User (Active) {uuid.uuid4().hex[:8]}"
    print(f"\nInviting existing user '{user_email}' as '{user_name}' to create a session-wide active test user...")

    invitation = IndividualInvite(name=user_name, email=user_email, role="student", timelineAlgorithm=None)
    payload = InvitationsFormPayload(invitations_attributes=[invitation])

    created_user: CourseUser | None = None
    try:
        invite_response = course_api.user_invitations.invite_from_form(payload)
        created_user = invite_response.invitation_result.new_course_users[0]
        print(f"Successfully created active user with ID: {created_user.id}")
        yield created_user
    finally:
        if created_user:
            print(f"\nSession cleanup: Deleting temporary user with ID {created_user.id}...")
            try:
                course_api.users.delete(created_user.id)
                print(f"Successfully deleted user {created_user.id}.")
            except CoursemologyAPIError as e:
                print(f"ERROR: Cleanup failed for user {created_user.id}. Error: {e}")


@pytest.fixture(scope="function")
def pending_invitation(course_api: CourseAPI) -> Generator[UserInvitation]:
    """
    Creates a temporary pending invitation for a non-existent user.
    This fixture runs for each test function that needs it and cleans up immediately after.
    """
    user_email = f"test-user-{uuid.uuid4().hex}@example.com"
    user_name = "Test User (Pending)"
    print(f"\nCreating pending invitation for new user '{user_email}'...")

    invitation = IndividualInvite(name=user_name, email=user_email, role="student", timelineAlgorithm=None)
    payload = InvitationsFormPayload(invitations_attributes=[invitation])

    created_invitation: UserInvitation | None = None
    try:
        invite_response = course_api.user_invitations.invite_from_form(payload)
        created_invitation = invite_response.invitation_result.new_invitations[0]
        print(f"Successfully created pending invitation with ID: {created_invitation.id}")
        yield created_invitation
    finally:
        if created_invitation:
            print(f"Function cleanup: Deleting pending invitation {created_invitation.id}...")
            try:
                course_api.user_invitations.delete(created_invitation.id)
                print(f"Successfully deleted pending invitation {created_invitation.id}.")
            except CoursemologyAPIError as e:
                print(f"ERROR: Cleanup failed for invitation {created_invitation.id}. Error: {e}")


@pytest.fixture(scope="session")
def test_tab(course_api: CourseAPI) -> TabBasic:
    """
    A session-scoped fixture that finds a valid assessment tab to be used
    for creating test assessments. Skips all dependent tests if no tabs are found.
    """
    print("\nFetching assessment categories to find a valid tab...")
    categories_response = course_api.assessment.categories.index()
    for category in categories_response.categories:
        if category.tabs:
            valid_tab = category.tabs[0]
            print(f"Found valid tab '{valid_tab.title}' (ID: {valid_tab.id}) for tests.")
            return valid_tab

    pytest.skip("Could not find any assessment tabs in the course. Skipping assessment tests.")


# --- Module-scoped aliases for session fixtures ---


@pytest.fixture(scope="module")
def course_api_module(course_api: CourseAPI) -> CourseAPI:
    """Module-scoped alias for the session-scoped course_api fixture."""
    return course_api


@pytest.fixture(scope="module")
def test_tab_module(test_tab: TabBasic) -> TabBasic:
    """Module-scoped alias for the session-scoped test_tab fixture."""
    return test_tab