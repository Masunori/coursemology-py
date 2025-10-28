from pydantic import BaseModel, Field


class Job(BaseModel):
    """
    Represents the detailed status of a background job, typically fetched by
    polling the URL from a `JobSubmitted` response.

    This model contains the full status information, any potential error messages,
    and a redirect URL upon completion (e.g., for a file download).
    """

    status: str  # e.g., 'submitted', 'running', 'completed', 'errored'
    error: str | None = None
    redirect_url: str | None = Field(None, alias="redirectUrl")
