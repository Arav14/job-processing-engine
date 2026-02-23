from typing import Dict, Optional
from app.models.job import Job


class JobRegistry:  # In-memory store for tracking jobs.
    def __init__(self):
        self._jobs: Dict[str, Job] = {}

    def add(self, job: Job) -> None:  # Add a job to the registry
        self._jobs[job.id] = job

    def get(self, job_id: str) -> Optional[Job]:  # Get a job from the registry
        return self._jobs.get(job_id)

    def list_all(self):  # List all jobs in the registry
        return list(self._jobs.values())
