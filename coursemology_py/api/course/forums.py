from typing import Literal

from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.auth import CoursemologySession
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.course.forums import (
    CreatePostResponse,
    DeletePostResponse,
    ForumFetchResponse,
    ForumListData,
    ForumPayload,
    ForumsIndexResponse,
    ForumTopicPostListData,
    MarkAnswerAndPublishResponse,
    PostPayload,
    PublishPostResponse,
    ToggleAnswerResponse,
    TopicFetchResponse,
    TopicPayload,
)


class ForumsAPI(BaseCourseAPI):
    """API handler for forums."""

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/forums"

    def index(self) -> ForumsIndexResponse:
        """Fetches a list of all forums in the course."""
        return self._get("", response_model=ForumsIndexResponse)

    def fetch(self, forum_id: int) -> ForumFetchResponse:
        """Fetches an existing forum and its topics."""
        return self._get(f"{forum_id}", response_model=ForumFetchResponse)

    def create(self, payload: ForumPayload) -> ForumListData:
        """Creates a new forum."""
        request_body = {"forum": payload.model_dump(by_alias=True)}
        return self._post("", json=request_body, response_model=ForumListData)

    def update(self, forum_id: int, payload: ForumPayload) -> ForumListData:
        """Updates an existing forum."""
        request_body = {"forum": payload.model_dump(by_alias=True)}
        return self._patch(f"{forum_id}", json=request_body, response_model=ForumListData)

    def delete(self, forum_id: int) -> None:
        """Deletes an existing forum."""
        self._delete(f"{forum_id}")

    def update_subscription(self, forum_id: int, subscribe: bool) -> None:
        """Updates the subscription status for a forum."""
        if subscribe:
            self._post(f"{forum_id}/subscribe")
        else:
            self._delete(f"{forum_id}/unsubscribe")

    def mark_all_as_read(self) -> None:
        """Marks all topics in all forums as read."""
        self._patch("mark_all_as_read")

    def mark_as_read(self, forum_id: int) -> None:
        """Marks all topics in a specific forum as read."""
        self._patch(f"{forum_id}/mark_as_read")


class TopicsAPI(BaseCourseAPI):
    """API handler for forum topics."""

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/forums"

    def fetch(self, forum_id: int, topic_id: int) -> TopicFetchResponse:
        """Fetches an existing topic and its posts."""
        return self._get(f"{forum_id}/topics/{topic_id}", response_model=TopicFetchResponse)

    def create(self, forum_id: int, payload: TopicPayload) -> None:
        """Creates a new topic. This endpoint redirects, so no JSON is returned."""
        self._post(f"{forum_id}/topics", json={"topic": payload.model_dump(by_alias=True)})

    def update(self, forum_id: int, topic_id: int, payload: TopicPayload) -> None:
        """Updates an existing topic."""
        self._patch(f"{forum_id}/topics/{topic_id}", json={"topic": payload.model_dump(by_alias=True)})

    def delete(self, forum_id: int, topic_id: int) -> None:
        """Deletes an existing topic."""
        self._delete(f"{forum_id}/topics/{topic_id}")

    def update_subscription(self, forum_id: int, topic_id: int, subscribe: bool) -> None:
        """Updates the subscription status for a topic."""
        self._post(f"{forum_id}/topics/{topic_id}/subscribe", json={"subscribe": subscribe})

    def update_hidden(self, forum_id: int, topic_id: int, hide: bool) -> None:
        """Updates the hidden status of a topic."""
        self._patch(f"{forum_id}/topics/{topic_id}/hidden", json={"hidden": hide})

    def update_locked(self, forum_id: int, topic_id: int, lock: bool) -> None:
        """Updates the locked status of a topic."""
        self._patch(f"{forum_id}/topics/{topic_id}/locked", json={"locked": lock})


class PostsAPI(BaseCourseAPI):
    """API handler for forum posts."""

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/forums"

    def create(self, forum_id: int, topic_id: int, payload: PostPayload) -> CreatePostResponse:
        """Creates a new post within a topic."""
        return self._post(
            f"{forum_id}/topics/{topic_id}/posts",
            json={"discussion_post": payload.model_dump(by_alias=True)},
            response_model=CreatePostResponse,
        )

    def update(self, forum_id: int, topic_id: int, post_id: int, text: str) -> ForumTopicPostListData:
        """Updates an existing post."""
        payload = {"discussion_post": {"text": text}}
        return self._patch(
            f"{forum_id}/topics/{topic_id}/posts/{post_id}",
            json=payload,
            response_model=ForumTopicPostListData,
        )

    def delete(self, forum_id: int, topic_id: int, post_id: int) -> DeletePostResponse:
        """Deletes an existing post."""
        return self._delete(f"{forum_id}/topics/{topic_id}/posts/{post_id}", response_model=DeletePostResponse)

    def toggle_answer(self, forum_id: int, topic_id: int, post_id: int) -> ToggleAnswerResponse:
        """Marks or unmarks a post as the answer for a topic."""
        return self._put(
            f"{forum_id}/topics/{topic_id}/posts/{post_id}/toggle_answer", response_model=ToggleAnswerResponse
        )

    def mark_answer_and_publish(self, forum_id: int, topic_id: int, post_id: int) -> MarkAnswerAndPublishResponse:
        """Marks a drafted AI-generated post as the answer and publishes it."""
        return self._put(
            f"{forum_id}/topics/{topic_id}/posts/{post_id}/mark_answer_and_publish",
            response_model=MarkAnswerAndPublishResponse,
        )

    def vote(self, forum_id: int, topic_id: int, post_id: int, vote: Literal[-1, 0, 1]) -> ForumTopicPostListData:
        """Upvotes, downvotes, or unvotes a post."""
        return self._put(
            f"{forum_id}/topics/{topic_id}/posts/{post_id}/vote",
            json={"vote": vote},
            response_model=ForumTopicPostListData,
        )

    def publish(self, forum_id: int, topic_id: int, post_id: int) -> PublishPostResponse:
        """Publishes a drafted post."""
        return self._put(f"{forum_id}/topics/{topic_id}/posts/{post_id}/publish", response_model=PublishPostResponse)

    def generate_reply(self, forum_id: int, topic_id: int, post_id: int) -> JobSubmitted:
        """Triggers a job to generate an AI reply for a post."""
        return self._put(f"{forum_id}/topics/{topic_id}/posts/{post_id}/generate_reply", response_model=JobSubmitted)


class ForumAPI:
    """A namespace class that groups all forum-related API handlers."""

    def __init__(self, session: CoursemologySession, base_url: str, course_id: int):
        self.forums = ForumsAPI(session, base_url, course_id)
        self.topics = TopicsAPI(session, base_url, course_id)
        self.posts = PostsAPI(session, base_url, course_id)
