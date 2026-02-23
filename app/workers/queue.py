from queue import PriorityQueue
from typing import Optional

from app.models.job import Job


class JobQueue:  # Thread-safe priority queue for Job objects.
    def __init__(self):
        self._queue = PriorityQueue()

    # Add a job to the queue. Lower priority number = Higher priority
    def add_job(self, job: Job) -> None:
        self._queue.put(job)

    # Retrieve next job from queue. Blocks if empty.
    def get_job(self) -> Optional[Job]:
        return self._queue.get()

    def is_empty(self) -> bool:  # Check if the queue is empty
        return self._queue.empty()

    def size(self) -> int:  # Get the number of jobs in the queue
        return self._queue.qsize()
