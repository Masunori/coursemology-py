from pydantic import BaseModel, Field


class JobSubmitted(BaseModel):
    """
    Represents the immediate, synchronous response from an API call that
    initiates a background job.

    This model is used when the only information returned immediately is the URL
    to poll for the job's status.
    """

    job_url: str = Field(..., alias="jobUrl")
