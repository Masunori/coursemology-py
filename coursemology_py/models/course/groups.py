from typing import Literal

from pydantic import BaseModel, Field

from coursemology_py.models.course.users import CourseUser


class GroupPermissions(BaseModel):
    """Permissions for the groups component."""

    can_create: bool | None = Field(alias="canCreate", default=None)
    can_manage: bool | None = Field(alias="canManage", default=None)


class GroupCategoryBasic(BaseModel):
    """A basic representation of a group category."""

    id: int
    name: str


class GroupCategoryData(GroupCategoryBasic):
    """A detailed representation of a group category."""

    description: str | None = None


class GroupMember(BaseModel):
    """
    Represents a user within a group. This is a subset of the main CourseUser model.
    """

    id: int  # This is the CourseUser ID
    # user_id: int = Field(..., alias="userId")
    name: str
    is_phantom: bool = Field(..., alias="isPhantom")
    role: Literal["manager", "normal"] = Field(..., alias="groupRole")
    # name_link: str = Field(..., alias="nameLink")


class Group(BaseModel):
    """Represents a single group."""

    id: int
    name: str
    description: str | None = None
    members: list[GroupMember]


class GroupCategoriesIndexResponse(BaseModel):
    """Response for the group categories index endpoint."""

    group_categories: list[GroupCategoryBasic] = Field(..., alias="groupCategories")
    permissions: GroupPermissions


class GroupCategoryInfoResponse(BaseModel):
    """
    Response for fetching a single group category's info.
    The reference client shows 'groups' can be nested, but the primary structure
    is a flat list of groups for the category.
    """

    group_category: GroupCategoryData = Field(..., alias="groupCategory")
    groups: list[Group]


class GroupCourseUsersResponse(BaseModel):
    """Response for fetching course users available for a group."""

    users: list[CourseUser]


class SimpleIdResponse(BaseModel):
    """A simple response containing just an ID."""

    id: int


class CreateGroupsResponse(BaseModel):
    """Response for the create_groups endpoint."""

    groups: list[Group]
    failed: list[str]  # Assuming failed items are strings


class UpdateGroupResponse(BaseModel):
    """Response for updating a single group."""

    group: Group


# --- API Payload Models ---


class GroupCategoryPayload(BaseModel):
    """Payload for creating or updating a group category."""

    name: str
    description: str | None = None


class GroupPayload(BaseModel):
    """Payload for creating or updating a single group."""

    name: str
    description: str | None = None


class GroupMemberUpdate(BaseModel):
    """Payload for a single member in a group update."""

    id: int  # CourseUser ID
    role: Literal["manager", "normal"]


class GroupUpdate(BaseModel):
    """Payload for a single group in a members update."""

    id: int  # Group ID
    members: list[GroupMemberUpdate]


class UpdateGroupMembersPayload(BaseModel):
    """The main payload for updating members across multiple groups."""

    groups: list[GroupUpdate]
