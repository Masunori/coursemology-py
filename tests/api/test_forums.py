import uuid
from collections.abc import Generator

import pytest
from coursemology_py.api.course import CourseAPI
from coursemology_py.exceptions import CoursemologyAPIError
from coursemology_py.models.course.forums import (
    ForumListData,
    ForumPayload,
    ForumTopicListData,
    ForumTopicPostListData,
    PostPayload,
    TopicPayload,
    TopicPostAttribute,
)

# --- Fixtures for Managed Forum Resources ---


@pytest.fixture(scope="module")
def test_forum(course_api: CourseAPI) -> Generator[ForumListData]:
    """
    A module-scoped fixture that creates a single, temporary forum for all
    tests in this module. It is cleaned up at the end of the module's run.
    """
    unique_title = f"Test Forum {uuid.uuid4().hex[:8]}"
    print(f"\nCreating temporary forum '{unique_title}' for module...")

    payload = ForumPayload(
        name=unique_title,
        description="A temporary forum for automated tests.",
        forum_topics_auto_subscribe=False,
    )
    created_forum: ForumListData | None = None
    try:
        created_forum = course_api.forums.forums.create(payload)
        print(f"Successfully created forum with ID: {created_forum.id}")
        yield created_forum
    finally:
        if created_forum:
            print(f"\nModule cleanup: Deleting forum with ID {created_forum.id}...")
            try:
                course_api.forums.forums.delete(created_forum.id)
                print(f"Successfully deleted forum {created_forum.id}.")
            except CoursemologyAPIError as e:
                pytest.fail(f"Module cleanup failed: Could not delete forum {created_forum.id}. Error: {e}")


@pytest.fixture(scope="function")
def test_topic(course_api: CourseAPI, test_forum: ForumListData) -> Generator[ForumTopicListData]:
    """
    A function-scoped fixture that creates a new topic within the module's
    test_forum. It is cleaned up after each test function.
    """
    unique_title = f"Test Topic {uuid.uuid4().hex[:8]}"
    print(f"\nCreating temporary topic '{unique_title}' for test...")

    post_attr = TopicPostAttribute(text="Initial post in the topic.", is_anonymous=False)
    payload = TopicPayload(
        title=unique_title,
        topic_type="normal",
        is_anonymous=False,
        posts_attributes=[post_attr],
    )
    created_topic: ForumTopicListData | None = None
    try:
        # The create topic endpoint redirects and doesn't return the object.
        # We must fetch the forum again to find the topic we just created.
        course_api.forums.topics.create(test_forum.id, payload)
        forum_details = course_api.forums.forums.fetch(test_forum.id)
        created_topic = next((t for t in forum_details.topics if t.title == unique_title), None)
        assert created_topic is not None, "Failed to find the newly created topic after creation."
        print(f"Successfully created topic with ID: {created_topic.id}")
        yield created_topic
    finally:
        if created_topic:
            print(f"Function cleanup: Deleting topic {created_topic.id}...")
            course_api.forums.topics.delete(test_forum.id, created_topic.id)
            print(f"Successfully deleted topic {created_topic.id}.")


@pytest.fixture(scope="function")
def test_post(
    course_api: CourseAPI, test_forum: ForumListData, test_topic: ForumTopicListData
) -> Generator[ForumTopicPostListData]:
    """
    A function-scoped fixture that creates a new post within the function's
    test_topic. Cleanup is handled by the test_topic fixture's teardown.
    """
    unique_text = f"Test reply post {uuid.uuid4().hex[:8]}"
    print(f"\nCreating temporary post '{unique_text[:20]}...' for test...")

    payload = PostPayload(text=unique_text, is_anonymous=False)
    response = course_api.forums.posts.create(test_forum.id, test_topic.id, payload)
    created_post = response.post
    print(f"Successfully created post with ID: {created_post.id}")
    yield created_post


# --- Forum API Tests ---


@pytest.mark.dependency()
def test_forum_create(test_forum: ForumListData):
    """Tests forum creation (implicitly via the fixture)."""
    assert isinstance(test_forum, ForumListData)
    assert "Test Forum" in test_forum.name


@pytest.mark.dependency(depends=["test_forum_create"])
def test_forum_fetch(course_api: CourseAPI, test_forum: ForumListData):
    """Tests fetching a specific forum."""
    response = course_api.forums.forums.fetch(test_forum.id)
    assert response.forum.id == test_forum.id
    assert response.forum.name == test_forum.name


@pytest.mark.dependency(depends=["test_forum_create"])
def test_forum_update(course_api: CourseAPI, test_forum: ForumListData):
    """Tests updating a forum's name and description."""
    updated_name = f"Updated Forum {uuid.uuid4().hex[:8]}"
    payload = ForumPayload(
        name=updated_name,
        description="This forum has been updated.",
        forum_topics_auto_subscribe=True,
    )
    response = course_api.forums.forums.update(test_forum.id, payload)
    assert response.name == updated_name
    assert response.description == "This forum has been updated."


# --- Topic API Tests ---


@pytest.mark.dependency(depends=["test_forum_fetch"])
def test_topic_create(test_topic: ForumTopicListData):
    """Tests topic creation (implicitly via the fixture)."""
    assert isinstance(test_topic, ForumTopicListData)
    assert "Test Topic" in test_topic.title


@pytest.mark.dependency(depends=["test_topic_create"])
def test_topic_fetch(course_api: CourseAPI, test_forum: ForumListData, test_topic: ForumTopicListData):
    """Tests fetching a specific topic."""
    response = course_api.forums.topics.fetch(test_forum.id, test_topic.id)
    assert response.topic.id == test_topic.id
    assert response.topic.title == test_topic.title


@pytest.mark.dependency(depends=["test_topic_create"])
def test_topic_lock_and_hide(course_api: CourseAPI, test_forum: ForumListData, test_topic: ForumTopicListData):
    """Tests locking, unlocking, hiding, and unhiding a topic."""
    # Test locking
    course_api.forums.topics.update_locked(test_forum.id, test_topic.id, lock=True)
    fetched_topic = course_api.forums.topics.fetch(test_forum.id, test_topic.id).topic
    assert fetched_topic.is_locked is True

    # Test hiding
    course_api.forums.topics.update_hidden(test_forum.id, test_topic.id, hide=True)
    fetched_topic = course_api.forums.topics.fetch(test_forum.id, test_topic.id).topic
    assert fetched_topic.is_hidden is True


# --- Post API Tests ---


@pytest.mark.dependency(depends=["test_topic_fetch"])
def test_post_create(test_post: ForumTopicPostListData):
    """Tests post creation (implicitly via the fixture)."""
    assert isinstance(test_post, ForumTopicPostListData)
    assert "Test reply post" in test_post.text


@pytest.mark.dependency(depends=["test_post_create"])
def test_post_update(
    course_api: CourseAPI, test_forum: ForumListData, test_topic: ForumTopicListData, test_post: ForumTopicPostListData
):
    """Tests updating a post's text."""
    updated_text = f"Updated post text {uuid.uuid4().hex[:8]}"
    response = course_api.forums.posts.update(test_forum.id, test_topic.id, test_post.id, updated_text)
    assert response.text == updated_text


@pytest.mark.dependency(depends=["test_post_create"])
def test_post_vote(
    course_api: CourseAPI, test_forum: ForumListData, test_topic: ForumTopicListData, test_post: ForumTopicPostListData
):
    """Tests upvoting, downvoting, and un-voting a post."""
    # Upvote
    response = course_api.forums.posts.vote(test_forum.id, test_topic.id, test_post.id, vote=1)
    assert response.vote_tally == 1
    assert response.has_user_voted is True

    # Un-vote
    response = course_api.forums.posts.vote(test_forum.id, test_topic.id, test_post.id, vote=0)
    assert response.vote_tally == 0
    assert response.has_user_voted is False


@pytest.mark.dependency(depends=["test_post_create"])
def test_post_delete(course_api: CourseAPI, test_forum: ForumListData, test_topic: ForumTopicListData):
    """Tests explicit deletion of a post."""
    payload = PostPayload(text="This post will be deleted.", is_anonymous=False)
    post_to_delete = course_api.forums.posts.create(test_forum.id, test_topic.id, payload).post

    # Delete the post
    delete_response = course_api.forums.posts.delete(test_forum.id, test_topic.id, post_to_delete.id)

    # Verify it's gone from the post tree
    post_ids_flat = [
        item
        for sublist in delete_response.post_tree_ids.root
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]  # pyright: ignore[reportUnknownVariableType]
    assert post_to_delete.id not in post_ids_flat
