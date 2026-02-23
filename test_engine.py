import time

from app.models.job import Job
from app.workers.queue import JobQueue
from app.workers.worker import Worker


def main():
    # Create queue
    queue = JobQueue()

    # Choose execution mode: "thread" or "process"
    execution_mode = "process"   # change to "thread" if needed

    # Create worker
    worker = Worker(queue, max_workers=3, mode=execution_mode)

    # Start worker
    worker.start()

    # Store jobs so we can inspect results later
    jobs = []

    # Add some jobs
    for i in range(5):
        job = Job(priority=i, name=f"job-{i}", payload=f"data-{i}")
        queue.add_job(job)
        jobs.append(job)
        print(f"Added job {job.id}")

    # Allow time for processing
    time.sleep(6)

    # Stop worker
    worker.stop()

    print("\nFinal Job Results:")
    for job in jobs:
        print(
            f"Job {job.id} | Status: {job.status} | Result: {job.result}"
        )


if __name__ == "__main__":
    main()
