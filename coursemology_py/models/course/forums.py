from __future__ import annotations

from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel, Field, RootModel

# --- Type Aliases and Enums ---
TopicType = Literal["normal", "question", "sticky", "announcement"]
PostWorkflowState = Literal["draft", "published"]


# --- RootModel for Recursive Type ---
# This creates a concrete Pydantic type for the recursive list,
# which prevents the RecursionError during import and type resolution.
class PostTree(RootModel[list[Union[int, "PostTree"]]]):
    pass


# --- Nested/Shared Models ---


class EmailSubscriptionSetting(BaseModel):
    is_course_email_setting_enabled: bool = Field(..., alias="isCourseEmailSettingEnabled")
    is_user_email_setting_enabled: bool = Field(..., alias="isUserEmailSettingEnabled")
    is_user_subscribed: bool = Field(..., alias="isUserSubscribed")
    manage_email_subscription_url: str | None = Field(None, alias="manageEmailSubscriptionUrl")


class PostCreator(BaseModel):
    id: int
    name: str
    user_url: str = Field(..., alias="userUrl")
    image_url: str = Field(..., alias="imageUrl")


class PostCreatorData(BaseModel):
    is_anonymous: bool = Field(..., alias="isAnonymous")
    creator: PostCreator | None = None
    created_at: datetime = Field(..., alias="createdAt")
    permissions: dict[str, bool]


class ForumPermissions(BaseModel):
    can_create_forum: bool = Field(..., alias="canCreateForum")


class ForumListDataPermissions(BaseModel):
    can_create_topic: bool | None = Field(None, alias="canCreateTopic")
    can_edit_forum: bool = Field(..., alias="canEditForum")
    can_delete_forum: bool = Field(..., alias="canDeleteForum")
    is_anonymous_enabled: bool | None = Field(alias="isAnonymousEnabled", default=None)


class ForumTopicListDataPermissions(BaseModel):
    can_edit_topic: bool = Field(..., alias="canEditTopic")
    can_delete_topic: bool = Field(..., alias="canDeleteTopic")
    can_subscribe_topic: bool = Field(..., alias="canSubscribeTopic")
    can_set_hidden_topic: bool = Field(..., alias="canSetHiddenTopic")
    can_set_locked_topic: bool = Field(..., alias="canSetLockedTopic")
    can_reply_topic: bool = Field(..., alias="canReplyTopic")
    can_toggle_answer: bool = Field(..., alias="canToggleAnswer")
    is_anonymous_enabled: bool | None = Field(alias="isAnonymousEnabled", default=None)
    can_manage_ai_response: bool = Field(..., alias="canManageAIResponse")


class ForumTopicPostListDataPermissions(BaseModel):
    can_edit_post: bool = Field(..., alias="canEditPost")
    can_delete_post: bool = Field(..., alias="canDeletePost")
    can_reply_post: bool = Field(..., alias="canReplyPost")
    can_view_anonymous: bool = Field(..., alias="canViewAnonymous")
    is_anonymous_enabled: bool | None = Field(alias="isAnonymousEnabled", default=None)


# --- Main Data Models ---


class ForumListData(BaseModel):
    id: int
    name: str
    description: str
    topic_unread_count: int = Field(..., alias="topicUnreadCount")
    forum_topics_auto_subscribe: bool = Field(..., alias="forumTopicsAutoSubscribe")
    root_forum_url: str = Field(..., alias="rootForumUrl")
    forum_url: str = Field(..., alias="forumUrl")
    is_unresolved: bool = Field(..., alias="isUnresolved")
    topic_count: int = Field(..., alias="topicCount")
    topic_post_count: int = Field(..., alias="topicPostCount")
    topic_view_count: int = Field(..., alias="topicViewCount")
    email_subscription: EmailSubscriptionSetting = Field(..., alias="emailSubscription")
    permissions: ForumListDataPermissions


class ForumTopicListData(BaseModel):
    id: int
    forum_id: int = Field(..., alias="forumId")
    title: str
    topic_url: str = Field(..., alias="topicUrl")
    is_unread: bool = Field(..., alias="isUnread")
    is_locked: bool = Field(..., alias="isLocked")
    is_hidden: bool = Field(..., alias="isHidden")
    is_resolved: bool = Field(..., alias="isResolved")
    topic_type: TopicType = Field(..., alias="topicType")
    vote_count: int = Field(..., alias="voteCount")
    post_count: int = Field(..., alias="postCount")
    view_count: int = Field(..., alias="viewCount")
    first_post_creator: PostCreatorData | None = Field(None, alias="firstPostCreator")
    latest_post_creator: PostCreatorData | None = Field(None, alias="latestPostCreator")
    email_subscription: EmailSubscriptionSetting = Field(..., alias="emailSubscription")
    permissions: ForumTopicListDataPermissions
    next_unread_topic_url: str | None = Field(None, alias="nextUnreadTopicUrl")
    forum_url: str = Field(..., alias="forumUrl")


class ForumTopicPostListData(BaseModel):
    id: int
    topic_id: int = Field(..., alias="topicId")
    parent_id: int | None = Field(None, alias="parentId")
    post_url: str = Field(..., alias="postUrl")
    text: str
    created_at: datetime = Field(..., alias="createdAt")
    is_answer: bool = Field(..., alias="isAnswer")
    is_unread: bool = Field(..., alias="isUnread")
    has_user_voted: bool = Field(..., alias="hasUserVoted")
    user_vote_flag: bool | None = Field(None, alias="userVoteFlag")
    vote_tally: int = Field(..., alias="voteTally")
    is_anonymous: bool = Field(..., alias="isAnonymous")
    creator: PostCreator | None = None
    is_ai_generated: bool = Field(..., alias="isAiGenerated")
    workflow_state: PostWorkflowState = Field(..., alias="workflowState")
    permissions: ForumTopicPostListDataPermissions


class ForumData(ForumListData):
    available_topic_types: list[TopicType] = Field(..., alias="availableTopicTypes")
    topic_ids: list[int] = Field(..., alias="topicIds")
    next_unread_topic_url: str | None = Field(None, alias="nextUnreadTopicUrl")


class ForumTopicData(ForumTopicListData):
    pass


# --- API Response Models ---


class ForumMetadata(BaseModel):
    next_unread_topic_url: str | None = Field(None, alias="nextUnreadTopicUrl")


class ForumsIndexResponse(BaseModel):
    forum_title: str = Field(..., alias="forumTitle")
    forums: list[ForumListData]
    metadata: ForumMetadata
    permissions: ForumPermissions


class ForumFetchResponse(BaseModel):
    forum: ForumData
    topics: list[ForumTopicListData]


class TopicFetchResponse(BaseModel):
    topic: ForumTopicData
    post_tree_ids: PostTree = Field(..., alias="postTreeIds")
    next_unread_topic_url: str | None = Field(None, alias="nextUnreadTopicUrl")
    posts: list[ForumTopicPostListData]


class CreatePostResponse(BaseModel):
    post: ForumTopicPostListData
    post_tree_ids: PostTree = Field(..., alias="postTreeIds")


class DeletePostResponse(BaseModel):
    is_topic_resolved: bool | None = Field(None, alias="isTopicResolved")
    is_topic_deleted: bool | None = Field(None, alias="isTopicDeleted")
    topic_id: int = Field(..., alias="topicId")
    post_tree_ids: PostTree = Field(..., alias="postTreeIds")


class ToggleAnswerResponse(BaseModel):
    is_topic_resolved: bool = Field(..., alias="isTopicResolved")


class MarkAnswerAndPublishResponse(BaseModel):
    workflow_state: PostWorkflowState = Field(..., alias="workflowState")
    is_topic_resolved: bool = Field(..., alias="isTopicResolved")
    creator: PostCreator


class PublishPostResponse(BaseModel):
    workflow_state: PostWorkflowState = Field(..., alias="workflowState")
    creator: PostCreator


# --- API Payload Models ---


class ForumPayload(BaseModel):
    name: str
    description: str | None = None
    forum_topics_auto_subscribe: bool = Field(alias="forum_topics_auto_subscribe", default=True)


class TopicPostAttribute(BaseModel):
    text: str
    is_anonymous: bool


class TopicPayload(BaseModel):
    title: str
    topic_type: TopicType = Field(..., alias="topic_type")
    is_anonymous: bool
    posts_attributes: list[TopicPostAttribute] = Field(..., alias="posts_attributes")


class PostPayload(BaseModel):
    text: str
    parent_id: int | None = Field(alias="parent_id", default=None)
    is_anonymous: bool | None = None
