from pydantic import BaseModel, Field


class TabBasic(BaseModel):
    """A minimal representation of a tab for the index endpoint."""

    id: int
    title: str
    weight: int


class CategoryBasic(BaseModel):
    """A minimal representation of a category for the index endpoint."""

    id: int
    title: str
    weight: int
    tabs: list[TabBasic]


class Tab(BaseModel):
    """
    Represents a single tab within an assessment category.
    Corresponds to `AssessmentTab` in TypeScript.
    """

    id: int
    title: str
    weight: int
    category_id: int = Field(..., alias="categoryId")
    assessments_count: int = Field(..., alias="assessmentsCount")
    top_assessment_titles: list[str] = Field(..., alias="topAssessmentTitles")
    full_tab_title: str | None = Field(None, alias="fullTabTitle")
    can_delete_tab: bool | None = Field(None, alias="canDeleteTab")


class Category(BaseModel):
    """
    Represents a single assessment category, containing multiple tabs.
    Corresponds to `AssessmentCategory` in TypeScript.
    """

    id: int
    title: str
    weight: int
    tabs: list[Tab]
    assessments_count: int = Field(..., alias="assessmentsCount")
    top_assessment_titles: list[str] = Field(..., alias="topAssessmentTitles")
    can_create_tabs: bool = Field(..., alias="canCreateTabs")
    can_delete_category: bool = Field(..., alias="canDeleteCategory")


class CategoriesIndexResponse(BaseModel):
    """The response object for the categories index endpoint."""

    categories: list[CategoryBasic]
