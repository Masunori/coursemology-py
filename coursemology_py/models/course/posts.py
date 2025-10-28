from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# --- Type Aliases and Enums ---
PostWorkflowState = Literal["draft", "published"]

# --- Nested/Shared Models ---


class PostCreator(BaseModel):
    """
    Represents the user who created the post.
    Corresponds to `CourseUserBasicListData` in the TS types.
    """

    id: int
    name: str
    user_url: str = Field(..., alias="userUrl")
    image_url: str = Field(..., alias="imageUrl")


class CodaveriFeedback(BaseModel):
    """Represents feedback from Codaveri on a post."""

    id: int
    status: str
    original_feedback: str = Field(..., alias="originalFeedback")
    rating: int


# --- Main Data Models ---


class Post(BaseModel):
    """
    Represents a generic discussion post, often used for comments.
    Corresponds to `CommentPostListData` in TypeScript.
    """

    id: int
    topic_id: int = Field(..., alias="topicId")
    is_delayed: bool = Field(..., alias="isDelayed")
    creator: PostCreator
    created_at: datetime = Field(..., alias="createdAt")
    title: str
    text: str
    can_update: bool = Field(..., alias="canUpdate")
    can_destroy: bool = Field(..., alias="canDestroy")
    codaveri_feedback: CodaveriFeedback | None = Field(None, alias="codaveriFeedback")
    workflow_state: PostWorkflowState = Field(..., alias="workflowState")
    is_ai_generated: bool = Field(..., alias="isAiGenerated")


# --- API Payload Models ---


class PostUpdatePayload(BaseModel):
    """Payload for updating a post/comment."""

    text: str
