from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.workers.queue import JobQueue
from app.workers.worker import Worker
from app.services.job_registry import JobRegistry
from app.api.routes import router

# Global shared components
queue = JobQueue()
registry = JobRegistry()
worker = Worker(queue, max_workers=3, mode="process")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start worker on startup
    print("Starting worker...")
    worker.start()
    yield
    # Shutdown
    print("Stopping worker...")
    worker.stop()

app = FastAPI(title="Job Processing Engine", lifespan=lifespan)

# Store shared objects inside app state
app.state.queue = queue
app.state.registry = registry
app.state.worker = worker
app.include_router(router)
