from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.job_registry import JobRecord, job_registry
from app.database.connection import get_db
from app.database.models import JobStatus
from app.database.schemas import JobResponse
from app.dependencies import get_current_user

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _to_job_response(record: JobRecord) -> JobResponse:
    """Transforms an in-memory JobRecord into the public JobResponse schema."""
    return JobResponse(
        job_id=record.job_id,
        video_id=record.video_id,
        course_id=record.course_id,
        playlist_id=record.playlist_id,
        status=record.status,
        workflow_name=record.workflow_name,
        current_node=record.current_node,
        progress_percentage=record.progress_percentage,
        logs=[log.to_dict() if hasattr(log, "to_dict") else log for log in record.logs],
        error_message=record.error_message,
        started_at=record.started_at,
        completed_at=record.completed_at,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Polls real-time state, logs, and progress percentage of an asynchronous ingestion or agent workflow job."""
    record = job_registry.get_job(job_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found.",
        )
    return _to_job_response(record)


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    status_filter: Optional[JobStatus] = Query(None, alias="status"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[JobResponse]:
    """Returns all tracked background synthesis and ingestion jobs."""
    jobs = job_registry.get_all_jobs()
    if status_filter:
        jobs = [j for j in jobs if j.status == status_filter]

    # Sort descending by started_at
    jobs.sort(key=lambda x: x.started_at, reverse=True)
    return [_to_job_response(j) for j in jobs]
