import pytest
from coursemology_py import CoursemologyClient
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.courses import CoursesIndexResponse


def test_courses_index(authenticated_client: CoursemologyClient) -> None:
    """
    Tests that fetching the list of all courses returns a valid response.
    """
    try:
        # 1. Make the API call using the authenticated client from the fixture
        response = authenticated_client.courses.index()

        # 2. Assert the response type is correct
        # This validates that the JSON was parsed into the right Pydantic model.
        assert isinstance(response, CoursesIndexResponse), "The response should be an instance of CoursesIndexResponse."

        # 3. Assert the structure and types of the data
        assert isinstance(response.courses, list), "The 'courses' attribute should be a list."
        assert isinstance(response.permissions.can_create, bool), "Permissions should be correctly parsed."

        # Optional: Check for at least one course if the test user is enrolled
        if response.courses:
            first_course = response.courses[0]
            assert isinstance(first_course.id, int)
            assert isinstance(first_course.title, str)

        print(f"\nSuccessfully fetched {len(response.courses)} courses.")

    except CoursemologyAPIError as e:
        pytest.fail(f"API call to courses.index() failed with an error: {e}")
