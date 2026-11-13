import asyncio
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from app.database.models import JobStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class JobLog:
    timestamp: str
    node: str
    message: str
    level: str = "info"  # "info" | "warning" | "error"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "node": self.node,
            "message": self.message,
            "level": self.level,
        }


@dataclass
class JobRecord:
    job_id: str
    video_id: Optional[str]
    course_id: Optional[str]
    playlist_id: Optional[str]
    status: JobStatus
    workflow_name: str
    current_node: str
    progress_percentage: int
    logs: List[JobLog] = field(default_factory=list)
    error_message: Optional[str] = None
    started_at: datetime = field(default_factory=utc_now)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "video_id": self.video_id,
            "course_id": self.course_id,
            "playlist_id": self.playlist_id,
            "status": self.status,
            "workflow_name": self.workflow_name,
            "current_node": self.current_node,
            "progress_percentage": self.progress_percentage,
            "logs": [log.to_dict() if isinstance(log, JobLog) else log for log in self.logs],
            "error_message": self.error_message,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class JobRegistry:
    """
    Thread-safe in-memory job registry for tracking asynchronous
    ingestion and agent pipeline execution progress.
    """

    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = threading.Lock()
        self._seed_default_jobs()

    def _seed_default_jobs(self) -> None:
        """Seed demo jobs for active polling and UI testing."""
        demo_job = JobRecord(
            job_id="job_demo_active",
            video_id="vid_ml_01",
            course_id="crs_ml_101",
            playlist_id=None,
            status=JobStatus.IN_PROGRESS,
            workflow_name="youtube_synthesis_pipeline",
            current_node="verify_notes",
            progress_percentage=75,
            logs=[
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node="ingest_video",
                    message="Video transcript fetched and normalized",
                    level="info",
                ),
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node="extract_structure",
                    message="Extracted 3 lecture modules",
                    level="info",
                ),
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node="generate_notes",
                    message="Multi-tier notes synthesized",
                    level="info",
                ),
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node="verify_notes",
                    message="Verifying mathematical derivations",
                    level="info",
                ),
            ],
            started_at=utc_now(),
        )
        self._jobs[demo_job.job_id] = demo_job

    def create_job(
        self,
        workflow_name: str,
        video_id: Optional[str] = None,
        course_id: Optional[str] = None,
        playlist_id: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> JobRecord:
        jid = job_id or f"job_{uuid.uuid4().hex[:12]}"
        record = JobRecord(
            job_id=jid,
            video_id=video_id,
            course_id=course_id or f"crs_{uuid.uuid4().hex[:10]}",
            playlist_id=playlist_id,
            status=JobStatus.PENDING,
            workflow_name=workflow_name,
            current_node="queued",
            progress_percentage=0,
            logs=[
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node="queued",
                    message="Job queued for asynchronous execution",
                    level="info",
                )
            ],
            started_at=utc_now(),
        )
        with self._lock:
            self._jobs[jid] = record
        return record

    def update_progress(
        self,
        job_id: str,
        node: str,
        message: str,
        progress: int,
        level: str = "info",
    ) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = JobStatus.IN_PROGRESS
            job.current_node = node
            job.progress_percentage = min(max(progress, 0), 100)
            job.logs.append(
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node=node,
                    message=message,
                    level=level,
                )
            )

    def complete_job(
        self,
        job_id: str,
        message: str = "Pipeline processing completed successfully",
        result: Optional[Any] = None,
    ) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = JobStatus.COMPLETED
            job.current_node = "completed"
            job.progress_percentage = 100
            job.completed_at = utc_now()
            if result is not None:
                job.result = result
            job.logs.append(
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node="completed",
                    message=message,
                    level="info",
                )
            )

    def fail_job(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job.status = JobStatus.FAILED
            job.error_message = error
            job.completed_at = utc_now()
            job.logs.append(
                JobLog(
                    timestamp=utc_now().isoformat(),
                    node=job.current_node or "error",
                    message=f"Job failed: {error}",
                    level="error",
                )
            )

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        with self._lock:
            return self._jobs.get(job_id)

    def get_all_jobs(self) -> List[JobRecord]:
        with self._lock:
            return list(self._jobs.values())


# Global singleton instance
job_registry = JobRegistry()
