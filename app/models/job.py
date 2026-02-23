from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import uuid
import time

from app.core.enums import JobStatus


@dataclass(order=True)
class Job:  # Represents a unit of work in the system
    priority: int  # Used for sorting in PriorityQueue
    name: str  # Business field
    payload: Any
    # Unique identifier for the job. uuid is used to ensure uniqueness across distributed systems.
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    # Current status of the job
    status: JobStatus = field(default=JobStatus.PENDING)
    # Timestamp when the job was created. utcnow() is used to ensure consistency across time zones.
    created_at: datetime = field(default_factory=datetime.utcnow)
    # Result of the job execution, if applicable.
    result: Optional[Any] = field(default=None)

    # Runs immediately after the dataclass is initialized. Used for validation and checks that the priority is non-negative.
    def __post_init__(self):
        if self.priority < 0:
            raise ValueError("Priority cannot be negative")

    # Provide a string representation of the Job for debugging and logging purposes.
    def __repr__(self) -> str:
        return (
            f"<Job id = {self.id}"
            f"name = {self.name}"
            f"status = {self.status}>"
        )

    # Used to execute the job. Makes the job instance callable.
    def __call__(self):
        self.status = JobStatus.RUNNING
        try:
            # Simulate CPU-bound work
            total = 0
            for i in range(50_000_000):
                total += i

            self.result = total
            self.status = JobStatus.SUCCESS
        except Exception as e:
            self.status = JobStatus.FAILED
            self.result = str(e)
