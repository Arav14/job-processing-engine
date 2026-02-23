from enum import Enum


class JobStatus(str, Enum):  # Enum representing lifecycle states of a Job.
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
