from coursemology_py.api.base import BaseCourseAPI
from coursemology_py.models.course.comments import (
    CommentPost,
    CommentPostPayload,
    CommentsIndexResponse,
    FetchCommentDataResponse,
)


class CommentsAPI(BaseCourseAPI):
    """
    API handler for the main course comments component.
    Mirrors `coursemology2/client/app/api/course/Comments.ts`.
    """

    @property
    def _url_prefix(self) -> str:
        return f"{super()._url_prefix}/comments"

    def index(self) -> CommentsIndexResponse:
        """Fetches initial data for the comments tab, including permissions and settings."""
        return self._get("", response_model=CommentsIndexResponse)

    def fetch_comment_data(self, tab_value: str, page_num: int) -> FetchCommentDataResponse:
        """Fetches a list of comment topics and their posts for a specific tab."""
        return self._get(
            f"{tab_value}",
            params={"page_num": page_num},
            response_model=FetchCommentDataResponse,
        )

    def toggle_pending(self, topic_id: int) -> None:
        """Toggles the pending status of a comment topic."""
        self._patch(f"{topic_id}/toggle_pending")

    def mark_as_read(self, topic_id: int) -> None:
        """Marks a comment topic as read."""
        self._patch(f"{topic_id}/mark_as_read")

    def create(self, topic_id: int, payload: CommentPostPayload) -> CommentPost:
        """Creates a new post (comment) within a topic."""
        request_body = {"discussion_post": payload.model_dump(exclude_none=True)}
        return self._post(f"{topic_id}/posts", json=request_body, response_model=CommentPost)

    def update(self, topic_id: int, post_id: int, payload: CommentPostPayload) -> CommentPost:
        """Updates an existing post (comment)."""
        request_body = {"discussion_post": payload.model_dump(exclude_none=True)}
        return self._patch(f"{topic_id}/posts/{post_id}", json=request_body, response_model=CommentPost)

    def delete(self, topic_id: int, post_id: int, codaveri_rating: int | None = None) -> None:
        """
        Deletes a post (comment).

        Args:
            topic_id: The ID of the topic the post belongs to.
            post_id: The ID of the post to delete.
            codaveri_rating: An optional rating, sent in the request body.
        """
        params = {}
        if codaveri_rating is not None:
            params["codaveri_rating"] = codaveri_rating

        # The reference client sends this in the `data` field for a DELETE request,
        # which corresponds to the `json` parameter in our helper.
        self._delete(f"{topic_id}/posts/{post_id}", json=params if params else None)
