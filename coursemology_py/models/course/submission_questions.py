from datetime import datetime

from pydantic import BaseModel, Field

# --- Nested/Shared Models ---


class CommentCreator(BaseModel):
    """
    Represents the user who created the comment.
    Corresponds to `CourseUserBasicListData` in the TS types.
    """

    id: int
    name: str
    user_url: str = Field(..., alias="userUrl")
    image_url: str = Field(..., alias="imageUrl")


class Comment(BaseModel):
    """
    Represents a single comment on a submission question.
    Corresponds to `CommentItem` in TypeScript.
    """

    id: int
    created_at: datetime = Field(..., alias="createdAt")
    creator: CommentCreator
    is_delayed: bool = Field(..., alias="isDelayed")
    text: str


class PastAnswer(BaseModel):
    """
    Represents a record of a past answer for viewing history.
    Corresponds to `AllAnswerItem` in TypeScript.
    """

    id: int
    created_at: datetime = Field(..., alias="createdAt")
    current_answer: bool = Field(..., alias="currentAnswer")
    workflow_state: str = Field(..., alias="workflowState")


# --- Main Response Model ---


class SubmissionQuestionDetails(BaseModel):
    """
    The response object for the submission question details endpoint.
    """

    all_answers: list[PastAnswer] = Field(..., alias="allAnswers")
    comments: list[Comment]
    can_view_history: bool = Field(..., alias="canViewHistory")


# --- API Payload and Response Models for Actions ---


class CommentPayload(BaseModel):
    """Payload for creating a new comment on a submission question."""

    text: str


class SubmissionQuestionComment(BaseModel):
    """
    Represents the detailed comment object returned by the API after creation.
    This is a more detailed version than the `Comment` model above.
    """

    id: int
    topic_id: int = Field(..., alias="topicId")
    text: str
    creator: CommentCreator
    created_at: datetime = Field(..., alias="createdAt")
