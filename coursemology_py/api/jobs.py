import time
from urllib.parse import urlparse

from coursemology_py.api.base import BaseAPI
from coursemology_py.models.common import JobSubmitted
from coursemology_py.models.jobs import Job


class JobsAPI(BaseAPI):
    """
    API handler for checking and managing the status of background jobs.
    """

    def _get_relative_path(self, full_url: str) -> str:
        """Strips the host to get a relative path suitable for the base methods."""
        api_prefix = urlparse(self._base_url).path
        full_path = urlparse(full_url).path
        if full_path.startswith(api_prefix):
            return full_path[len(api_prefix) :]
        return full_path

    def fetch_status(self, job_url: str) -> Job:
        """
        Fetches the current status of a background job from its URL.

        Args:
            job_url: The full URL of the job to check.
        """
        relative_path = self._get_relative_path(job_url)
        return self._get(relative_path, response_model=Job)

    def wait_for_completion(
        self,
        submitted_job: JobSubmitted,
        timeout: int = 60,
        poll_interval: int = 2,
    ) -> Job:
        """
        Polls the job status until it is completed or errored, or until a timeout is reached.
        This is a convenience method that handles the polling loop for you.

        Args:
            submitted_job: The JobSubmitted object returned by an API call that starts a job.
            timeout: The maximum time to wait in seconds.
            poll_interval: The time to wait between polling attempts in seconds.

        Returns:
            The final state of the Job object once it is 'completed'.

        Raises:
            TimeoutError: If the job does not complete within the timeout period.
            RuntimeError: If the job completes with an 'errored' status.
        """
        print(f"Waiting for job at {submitted_job.job_url} to complete...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_job_status = self.fetch_status(submitted_job.job_url)
            print(f"  Current status: {current_job_status.status}")

            if current_job_status.status == "completed":
                print("Job completed successfully.")
                return current_job_status

            if current_job_status.status == "errored":
                raise RuntimeError(f"Job failed with error: {current_job_status.error}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Job did not complete within {timeout} seconds.")
