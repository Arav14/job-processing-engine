from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import uuid4

from app.db.deps import get_db
from app.db.models import JobDB
from app.workers.queue import JobQueue
from app.models.job import Job
from app.core.enums import JobStatus

router = APIRouter()


class JobCreateRequest(BaseModel):
    name: str
    priority: int = 0
    payload: str


@router.post("/jobs")
def create_job(request_data: JobCreateRequest, request: Request, db: Session = Depends(get_db)):  # Create a new job
    job_id = str(uuid4())

    db_job = JobDB(
        id=job_id,
        name=request_data.name,
        priority=request_data.priority,
        status=JobStatus.PENDING.value,
        payload=request_data.payload,
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    queue = request.app.state.queue
    queue.add_job(job_id)

    return {
        "message": "Job stored in DB and queued",
        "job_id": db_job.id,
        "status": db_job.status
    }


@router.get("/jobs/{job_id}")  # get the job from registry
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobDB).filter(JobDB.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "name": job.name,
        "status": job.status,
        "result": job.result,
    }


@router.get("/jobs")  # get all jobs from registry
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(JobDB).all()

    return [
        {
            "id": job.id,
            "name": job.name,
            "status": job.status,
            "result": job.result,
        }
        for job in jobs
    ]
