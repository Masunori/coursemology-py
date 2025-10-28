from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.posts import Post, PostUpdatePayload


class PostsAPI(BaseCourseAPI):
    """
    A minimal, generic API handler for updating and deleting discussion posts (comments).
    Mirrors `coursemology2/client/app/api/course/Posts.js`.
    """

    def _get_url(self, topic_id: int, post_id: int) -> str:
        """Constructs the specific URL for a post within a comment topic."""
        return f"{super()._url_prefix}/comments/{topic_id}/posts/{post_id}"

    def update(self, topic_id: int, post_id: int, payload: PostUpdatePayload) -> Post:
        """
        Updates a discussion post (comment).
        """
        request_body = {"discussion_post": payload.model_dump()}
        url = self._get_url(topic_id, post_id)
        return self._patch(url, json=request_body, response_model=Post)

    def delete(self, topic_id: int, post_id: int) -> None:
        """
        Deletes a discussion post (comment).
        """
        url = self._get_url(topic_id, post_id)
        self._delete(url)
