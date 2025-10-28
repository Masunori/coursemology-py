from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# Import the user model to represent the creator accurately
from coursemology_py.models.course.users import CourseUserBasic

# --- Type Aliases and Enums ---
PostWorkflowState = Literal["draft", "published"]

# --- Nested/Shared Models ---


class CommentPermissions(BaseModel):
    """
    Permissions for the main comments component.
    Corresponds to `CommentPermissions` in TypeScript.
    """

    can_manage: bool = Field(..., alias="canManage")
    is_student: bool = Field(..., alias="isStudent")
    is_teaching_staff: bool = Field(..., alias="isTeachingStaff")


class CommentSettings(BaseModel):
    """
    Settings for the main comments component.
    Corresponds to `CommentSettings` in TypeScript.
    """

    title: str
    topics_per_page: int = Field(..., alias="topicsPerPage")


class CommentTabInfo(BaseModel):
    """
    Represents the counts for different comment tabs.
    Corresponds to `CommentTabInfo` in TypeScript.
    """

    my_student_exist: bool | None = Field(None, alias="myStudentExist")
    my_student_unread_count: int | None = Field(None, alias="myStudentUnreadCount")
    all_staff_unread_count: int | None = Field(None, alias="allStaffUnreadCount")
    all_student_unread_count: int | None = Field(None, alias="allStudentUnreadCount")


class CommentTopicPermissions(BaseModel):
    can_toggle_pending: bool = Field(..., alias="canTogglePending")
    can_mark_as_read: bool = Field(..., alias="canMarkAsRead")


class CommentTopicSettings(BaseModel):
    is_pending: bool = Field(..., alias="isPending")
    is_unread: bool = Field(..., alias="isUnread")
    topic_count: int = Field(..., alias="topicCount")


class CommentLinks(BaseModel):
    title_link: str = Field(..., alias="titleLink")


class CodaveriFeedback(BaseModel):
    id: int
    status: str
    original_feedback: str = Field(..., alias="originalFeedback")
    rating: int


# --- Main Data Models ---


class CommentPost(BaseModel):
    """
    Represents a single post within a comment topic.
    Corresponds to `CommentPostListData` in TypeScript.
    """

    id: int
    topic_id: int = Field(..., alias="topicId")
    is_delayed: bool = Field(..., alias="isDelayed")
    creator: CourseUserBasic
    created_at: datetime = Field(..., alias="createdAt")
    title: str
    text: str
    can_update: bool = Field(..., alias="canUpdate")
    can_destroy: bool = Field(..., alias="canDestroy")
    codaveri_feedback: CodaveriFeedback | None = Field(None, alias="codaveriFeedback")
    workflow_state: PostWorkflowState = Field(..., alias="workflowState")
    is_ai_generated: bool = Field(..., alias="isAiGenerated")


class CommentTopic(BaseModel):
    """
    Represents a single topic in the comments list.
    Corresponds to `CommentTopicData` in TypeScript.
    """

    type: str
    id: int
    title: str
    creator: CourseUserBasic
    topic_permissions: CommentTopicPermissions = Field(..., alias="topicPermissions")
    topic_settings: CommentTopicSettings = Field(..., alias="topicSettings")
    post_list: list[CommentPost] = Field(..., alias="postList")
    links: CommentLinks
    content: str | None = None
    timestamp: datetime | None = None


# --- API Response Models ---


class CommentsIndexResponse(BaseModel):
    """
    Response for the main comments index endpoint.
    """

    permissions: CommentPermissions
    settings: CommentSettings
    tabs: CommentTabInfo


class FetchCommentDataResponse(BaseModel):
    """Response for fetching a list of comment topics."""

    topic_count: int = Field(..., alias="topicCount")
    topic_list: list[CommentTopic] = Field(..., alias="topicList")


# --- API Payload Models ---


class CommentPostPayload(BaseModel):
    """Payload for creating or updating a post in the comments component."""

    title: str | None = None
    text: str
