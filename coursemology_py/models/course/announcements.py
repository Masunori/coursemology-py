from datetime import datetime

from pydantic import BaseModel, Field

# --- Nested/Shared Models ---


class AnnouncementPermissions(BaseModel):
    """Permissions for a single announcement."""

    can_edit: bool = Field(..., alias="canEdit")
    can_delete: bool = Field(..., alias="canDelete")


class AnnouncementCreator(BaseModel):
    """Represents the user who created the announcement."""

    id: int
    name: str
    user_url: str | None = Field(None, alias="userUrl")
    image_url: str | None = Field(None, alias="imageUrl")


# --- Main Data Models ---


class Announcement(BaseModel):
    """
    Represents a single course announcement with all its details.
    Corresponds to `AnnouncementData` in TypeScript.
    """

    id: int
    title: str
    content: str
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime | None = Field(None, alias="endTime")
    is_unread: bool = Field(..., alias="isUnread")
    is_sticky: bool = Field(..., alias="isSticky")
    is_currently_active: bool = Field(..., alias="isCurrentlyActive")
    mark_as_read_url: str = Field(..., alias="markAsReadUrl")
    creator: AnnouncementCreator
    permissions: AnnouncementPermissions


class IndexPermissions(BaseModel):
    """
    Top-level permissions for the announcements component.
    Corresponds to `AnnouncementPermissions` in TypeScript.
    """

    can_create: bool = Field(..., alias="canCreate")


class AnnouncementsIndexResponse(BaseModel):
    """
    The response object for the announcements index endpoint.
    Corresponds to `FetchAnnouncementsData` in TypeScript.
    """

    announcement_title: str = Field(..., alias="announcementTitle")
    announcements: list[Announcement]
    permissions: IndexPermissions


# --- API Payload Models ---


class AnnouncementPayload(BaseModel):
    """
    A model representing the data payload for creating or updating an announcement.
    Corresponds to `AnnouncementFormData` in TypeScript.
    """

    title: str
    content: str
    sticky: bool
    start_at: datetime
    end_at: datetime | None = None
