import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, Future
from typing import Optional, Literal

from sqlalchemy.orm import Session

from app.workers.queue import JobQueue
from app.db.database import SessionLocal
from app.db.models import JobDB
from app.core.enums import JobStatus

# allowing only thread or process as valid execution modes
ExecutionMode = Literal["thread", "process"]


class Worker:  # Background worker that processes jobs concurrently. Supports both thread and process based execution.
    def __init__(self, queue, max_workers: int = 3, mode: ExecutionMode = "process"):
        self.queue = queue
        self._running = False  # Flag to control the worker loop
        # Thread that monitors the job queue
        self._monitor_thread: Optional[threading.Thread] = None
        self.mode = mode

        if mode == "thread":
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
        elif mode == "process":
            self.executor = ProcessPoolExecutor(max_workers=max_workers)
        else:
            raise ValueError("mode must be 'thread' or 'process'")

        print(
            f"Worker initialized with {mode} pool (max_workers={max_workers}).")

    # Start monitoring thread that submits jobs to thread pool.
    def start(self):
        self._running = True
        # Daemon thread will exit when main program exits
        self._monitor_thread = threading.Thread(target=self._run, daemon=True)
        self._monitor_thread.start()
        print("Worker started.")

    # Stop worker
    def stop(self):  # Stop the worker thread
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()  # Wait for the thread to finish

        self.executor.shutdown(wait=True)  # Cleanly shutdown the thread pool.
        print("Worker stopped.")

    # Continuously pull jobs from queue and submit to thread pool.
    def _run(self):
        while self._running:
            if not self.queue.is_empty():  # Check if there are jobs to process
                job_id = self.queue.get_job()  # Get next job from the queue
                print(f"Submitting job {job_id}")

                future = self.executor.submit(self._execute_job, job_id)

                future.add_done_callback(lambda f, job_id=job_id: self._handle_result(
                    job_id, f))  # Handle result when job is done

            else:
                # Sleep briefly to avoid busy waiting when queue is empty
                time.sleep(0.2)

    @staticmethod
    # Thread safe execution that mutates the job object directly.
    def _execute_job(job_id: str):
        db: Session = SessionLocal()

        try:
            job = db.query(JobDB).filter(JobDB.id == job_id).first()
            if not job:
                return "Job not found"

            if job.status == JobStatus.CANCELLED.value:
                return "Job cancelled"

            job.status = JobStatus.RUNNING
            db.commit()

            # Simulate CPU workload
            total = 0
            for i in range(50_000_000):
                total += i

            return str(total)

        finally:
            db.close()

    def _handle_result(self, job_id: str, future: Future):
        db: Session = SessionLocal()

        try:
            job = db.query(JobDB).filter(JobDB.id == job_id).first()
            if not job:
                return
        # Handles job completion safely in parent process
            try:
                result = future.result()  # get result from future

                if job.status != JobStatus.CANCELLED.value:
                    job.result = result
                    job.status = JobStatus.SUCCESS.value

            except Exception as e:
                job.status = JobStatus.FAILED
                job.result = str(e)

            db.commit()
            print(f"Completed job {job_id} with status {job.status}")

        finally:
            db.close()


if __name__ == "__main__":
    print("Starting Job worker...")

    queue = JobQueue()

    worker = Worker(
        queue=queue,
        max_workers=3,
        mode="process"
    )

    worker.start()

    # Keep worker alive
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        worker.stop()
