from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.database.schemas import ProgressResponse, ProgressUpdate
from app.dependencies import get_current_user

router = APIRouter(prefix="/progress", tags=["Learning Progress"])


@router.get("", response_model=List[ProgressResponse])
async def get_user_progress(
    course_id: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ProgressResponse]:
    """Retrieves learning progress for all courses or a single course."""
    now = datetime.now(timezone.utc)
    return [
        ProgressResponse(
            id="prog_001",
            user_id=current_user.id,
            course_id=course_id or "crs_ml_101",
            video_id="vid_ml_01",
            is_completed=True,
            last_position_seconds=780,
            notes_reviewed=True,
            quiz_completed=True,
            updated_at=now,
        ),
        ProgressResponse(
            id="prog_002",
            user_id=current_user.id,
            course_id=course_id or "crs_quantum_201",
            video_id="vid_quantum_01",
            is_completed=False,
            last_position_seconds=320,
            notes_reviewed=True,
            quiz_completed=False,
            updated_at=now,
        ),
    ]


@router.post("/{course_id}", response_model=ProgressResponse)
async def update_progress(
    course_id: str,
    update_data: ProgressUpdate,
    video_id: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProgressResponse:
    """Updates watch position and completion milestones."""
    now = datetime.now(timezone.utc)
    return ProgressResponse(
        id=f"prog_{course_id}",
        user_id=current_user.id,
        course_id=course_id,
        video_id=video_id,
        is_completed=update_data.is_completed or False,
        last_position_seconds=update_data.last_position_seconds or 0,
        notes_reviewed=update_data.notes_reviewed or False,
        quiz_completed=update_data.quiz_completed or False,
        updated_at=now,
    )


@router.get("/summary", response_model=Dict[str, Any])
async def get_progress_summary(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Returns aggregated student statistics for dashboard analytics."""
    return {
        "total_courses_enrolled": 3,
        "completed_courses": 1,
        "total_study_minutes": 340,
        "quizzes_taken": 12,
        "average_quiz_accuracy": 92.4,
        "flashcards_mastered": 48,
        "active_streak_days": 7,
        "retention_score": 94.8,
        "weekly_activity": [
            {"day": "Mon", "minutes": 45, "quizzes": 2},
            {"day": "Tue", "minutes": 60, "quizzes": 3},
            {"day": "Wed", "minutes": 30, "quizzes": 1},
            {"day": "Thu", "minutes": 75, "quizzes": 4},
            {"day": "Fri", "minutes": 50, "quizzes": 2},
            {"day": "Sat", "minutes": 40, "quizzes": 1},
            {"day": "Sun", "minutes": 40, "quizzes": 2},
        ],
    }
