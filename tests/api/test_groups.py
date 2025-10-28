import uuid
from collections.abc import Generator

import pytest
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.course.groups import (
    Group,
    GroupCategoryData,
    GroupCategoryPayload,
    GroupMemberUpdate,
    GroupPayload,
    GroupUpdate,
    UpdateGroupMembersPayload,
)
from coursemology_py.models.course.users import CourseUser

# --- Fixtures for Managed Group Resources ---


@pytest.fixture(scope="function")
def test_group_category(course_api: CourseAPI) -> Generator[GroupCategoryData]:
    """
    A function-scoped fixture that creates a temporary group category for a test
    and cleans it up afterward.
    """
    unique_name = f"Test Category {uuid.uuid4().hex[:8]}"
    print(f"\nCreating temporary group category '{unique_name}' for test...")

    payload = GroupCategoryPayload(name=unique_name, description="A temporary category for tests.")
    created_category: GroupCategoryData | None = None
    try:
        # The create endpoint only returns an ID, so we fetch the full object after.
        response = course_api.groups.create_category(payload)
        category_details = course_api.groups.fetch(response.id)
        created_category = category_details.group_category
        print(f"Successfully created group category with ID: {created_category.id}")
        yield created_category
    finally:
        if created_category:
            print(f"\nCleaning up: Deleting group category with ID {created_category.id}...")
            try:
                course_api.groups.delete_category(created_category.id)
                print(f"Successfully deleted group category {created_category.id}.")
            except CoursemologyAPIError as e:
                pytest.fail(f"Cleanup failed for group category {created_category.id}. Error: {e}")


@pytest.fixture(scope="function")
def test_group(course_api: CourseAPI, test_group_category: GroupCategoryData) -> Generator[Group]:
    """
    A function-scoped fixture that creates a temporary group inside the
    test_group_category. Cleanup is handled by the category's fixture.
    """
    unique_name = f"Test Group {uuid.uuid4().hex[:8]}"
    print(f"\nCreating temporary group '{unique_name}' for test...")

    payload = GroupPayload(name=unique_name, description="A temporary group for tests.")
    response = course_api.groups.create_groups(test_group_category.id, [payload])
    created_group = response.groups[0]
    print(f"Successfully created group with ID: {created_group.id}")
    yield created_group


# --- API Tests ---


def test_groups_fetch_group_categories(course_api: CourseAPI):
    """Tests fetching the index of all group categories."""
    response = course_api.groups.fetch_group_categories()
    assert response.permissions.can_create is True
    assert isinstance(response.group_categories, list)
    print(f"\nSuccessfully fetched {len(response.group_categories)} group categories.")


def test_group_category_create_and_fetch(course_api: CourseAPI, test_group_category: GroupCategoryData):
    """
    Tests category creation (via fixture) and fetching a specific category.
    """
    assert isinstance(test_group_category, GroupCategoryData)
    assert "Test Category" in test_group_category.name

    # Fetch the category again to verify
    response = course_api.groups.fetch(test_group_category.id)
    assert response.group_category.id == test_group_category.id
    assert response.group_category.name == test_group_category.name


def test_group_category_update(course_api: CourseAPI, test_group_category: GroupCategoryData):
    """Tests updating a group category's name and description."""
    updated_name = f"Updated Category {uuid.uuid4().hex[:8]}"
    payload = GroupCategoryPayload(name=updated_name, description="This category has been updated.")
    course_api.groups.update_category(test_group_category.id, payload)

    # Verify the update
    response = course_api.groups.fetch(test_group_category.id)
    assert response.group_category.name == updated_name
    assert response.group_category.description == "This category has been updated."
    print(f"\nSuccessfully updated group category {test_group_category.id}.")


def test_group_create(test_group: Group):
    """Tests group creation (implicitly via the fixture)."""
    assert isinstance(test_group, Group)
    assert "Test Group" in test_group.name


def test_group_update(course_api: CourseAPI, test_group_category: GroupCategoryData, test_group: Group):
    """Tests updating a group's name and description."""
    updated_name = f"Updated Group {uuid.uuid4().hex[:8]}"
    payload = GroupPayload(name=updated_name, description="This group has been updated.")
    course_api.groups.update_group(test_group_category.id, test_group.id, payload)

    # Verify the update
    response = course_api.groups.fetch(test_group_category.id)
    updated_group_from_api = next((g for g in response.groups if g.id == test_group.id), None)
    assert updated_group_from_api is not None
    assert updated_group_from_api.name == updated_name
    assert updated_group_from_api.description == "This group has been updated."
    print(f"\nSuccessfully updated group {test_group.id}.")


def test_group_delete(course_api: CourseAPI, test_group_category: GroupCategoryData):
    """Tests explicit deletion of a group within a category."""
    group_payloads = [
        GroupPayload(name=f"Group A {uuid.uuid4().hex[:4]}"),
        GroupPayload(name=f"Group B {uuid.uuid4().hex[:4]}"),
    ]
    created_groups = course_api.groups.create_groups(test_group_category.id, group_payloads)
    assert len(created_groups.groups) == 2
    group_to_delete = created_groups.groups[0]

    # Delete one group
    course_api.groups.delete_group(test_group_category.id, group_to_delete.id)
    print(f"\nDeleted group {group_to_delete.id}.")

    # Verify it's gone
    response = course_api.groups.fetch(test_group_category.id)
    group_ids = [g.id for g in response.groups]
    assert group_to_delete.id not in group_ids
    assert created_groups.groups[1].id in group_ids
    print("Verified group was successfully deleted from the category.")


def test_group_members_update(
    course_api: CourseAPI, test_group_category: GroupCategoryData, test_group: Group, test_user: CourseUser
):
    """Tests adding a user to a group and assigning a role."""
    # 1. Add the test_user to the group as a 'normal' member
    member_update = GroupMemberUpdate(id=test_user.id, role="normal")
    group_update = GroupUpdate(id=test_group.id, members=[member_update])
    payload = UpdateGroupMembersPayload(groups=[group_update])

    course_api.groups.update_group_members(test_group_category.id, payload)
    print(f"\nAdded user {test_user.id} to group {test_group.id}.")

    # 2. Verify the user is in the group
    response = course_api.groups.fetch(test_group_category.id)
    group_from_api = next((g for g in response.groups if g.id == test_group.id), None)
    assert group_from_api is not None
    member_from_api = next((m for m in group_from_api.members if m.id == test_user.id), None)
    assert member_from_api is not None, "Test user was not found in the group members list."
    assert member_from_api.role == "normal"
    print("Verified user is in the group with role 'normal'.")

    # 3. Remove the user from the group by submitting an empty members list
    group_update_empty = GroupUpdate(id=test_group.id, members=[])
    payload_empty = UpdateGroupMembersPayload(groups=[group_update_empty])
    course_api.groups.update_group_members(test_group_category.id, payload_empty)
    print(f"Removed user {test_user.id} from group {test_group.id}.")

    # 4. Verify the user is gone
    response_after_removal = course_api.groups.fetch(test_group_category.id)
    group_after_removal = next((g for g in response_after_removal.groups if g.id == test_group.id), None)
    assert group_after_removal is not None
    assert test_user.id not in [m.id for m in group_after_removal.members]
    print("Verified user was successfully removed from the group.")
