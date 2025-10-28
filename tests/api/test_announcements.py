import datetime
import uuid
from collections.abc import Generator

import pytest
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.course.announcements import (
    Announcement,
    AnnouncementPayload,
    AnnouncementsIndexResponse,
)

# --- Fixture for a temporary, managed announcement ---


@pytest.fixture(scope="function")
def test_announcement(course_api: CourseAPI) -> Generator[Announcement]:
    """
    A function-scoped fixture that creates a new, temporary announcement before
    a test runs and cleans it up immediately afterward.

    This provides a fresh, isolated resource for each test function.

    Yields:
        The created Announcement object.
    """
    unique_title = f"Test Announcement {uuid.uuid4().hex[:8]}"
    print(f"\nCreating temporary announcement '{unique_title}' for test...")

    payload = AnnouncementPayload(
        title=unique_title,
        content="<p>This is a temporary announcement created for an automated test.</p>",
        sticky=False,
        start_at=datetime.datetime.now(datetime.UTC),
    )

    created_announcement: Announcement | None = None
    try:
        # SETUP: Create the announcement
        created_announcement = course_api.announcements.create(payload)
        print(f"Successfully created announcement with ID: {created_announcement.id}")

        # Yield the object to the test function
        yield created_announcement

    finally:
        # TEARDOWN: Clean up the announcement
        if created_announcement:
            print(f"\nCleaning up: Deleting announcement with ID {created_announcement.id}...")
            try:
                course_api.announcements.delete(created_announcement.id)
                print(f"Successfully deleted announcement {created_announcement.id}.")
            except CoursemologyAPIError as e:
                # Fail the test if cleanup fails, as it indicates a problem with the delete API
                pytest.fail(f"Cleanup failed: Could not delete announcement {created_announcement.id}. Error: {e}")


# --- API Tests ---


def test_announcements_index(course_api: CourseAPI) -> None:
    """
    Tests that fetching the list of all announcements returns a valid response.
    """
    try:
        response = course_api.announcements.index()

        assert isinstance(response, AnnouncementsIndexResponse), (
            "Response should be an instance of AnnouncementsIndexResponse."
        )

        assert isinstance(response.announcements, list)
        assert isinstance(response.permissions.can_create, bool)

        if response.announcements:
            assert isinstance(response.announcements[0], Announcement)

        print(f"\nSuccessfully fetched {len(response.announcements)} announcements.")

    except CoursemologyAPIError as e:
        pytest.fail(f"API call to announcements.index() failed: {e}")


def test_announcement_create(test_announcement: Announcement) -> None:
    """
    Tests the successful creation of an announcement.

    The actual creation is handled by the `test_announcement` fixture. This test
    simply verifies that the object yielded by the fixture is valid, which
    implicitly confirms that the create operation was successful.
    """
    assert isinstance(test_announcement, Announcement)
    assert isinstance(test_announcement.id, int)
    assert "Test Announcement" in test_announcement.title
    assert test_announcement.is_sticky is False


def test_announcement_update(course_api: CourseAPI, test_announcement: Announcement) -> None:
    """
    Tests updating an existing announcement's title, content, and sticky status.
    """
    updated_title = f"Updated Title {uuid.uuid4().hex[:8]}"
    updated_content = "<p>This content has been updated by an automated test.</p>"

    # Prepare the update payload
    payload = AnnouncementPayload(
        title=updated_title,
        content=updated_content,
        sticky=True,  # Change sticky status from False to True
        start_at=test_announcement.start_time,
    )

    try:
        # Perform the update
        updated_response = course_api.announcements.update(test_announcement.id, payload)

        # Assert that the response reflects the changes
        assert isinstance(updated_response, Announcement)
        assert updated_response.id == test_announcement.id
        assert updated_response.title == updated_title
        assert updated_response.content == updated_content
        assert updated_response.is_sticky is True

        print(f"\nSuccessfully updated announcement {test_announcement.id}.")

    except CoursemologyAPIError as e:
        pytest.fail(f"API call to announcements.update() failed: {e}")


def test_announcement_delete(course_api: CourseAPI) -> None:
    """
    Tests the explicit deletion of an announcement.

    This test creates its own announcement, deletes it, and then verifies
    it is no longer present in the index list, providing a robust check of
    the delete functionality.
    """
    payload = AnnouncementPayload(
        title=f"To Be Deleted {uuid.uuid4().hex[:8]}",
        content="<p>This announcement will be deleted.</p>",
        sticky=False,
        start_at=datetime.datetime.now(datetime.UTC),
    )

    try:
        # 1. Create a new announcement specifically for this test
        announcement_to_delete = course_api.announcements.create(payload)
        print(f"\nCreated announcement {announcement_to_delete.id} for deletion test.")

        # 2. Delete it
        course_api.announcements.delete(announcement_to_delete.id)
        print(f"Deleted announcement {announcement_to_delete.id}.")

        # 3. Verify it's gone by fetching the index and checking for its ID
        all_announcements = course_api.announcements.index().announcements
        announcement_ids = [a.id for a in all_announcements]
        assert announcement_to_delete.id not in announcement_ids, "Deleted announcement ID should not be in the index."
        print("Verified that the announcement is no longer in the index.")

    except CoursemologyAPIError as e:
        pytest.fail(f"Explicit deletion test failed: {e}")
