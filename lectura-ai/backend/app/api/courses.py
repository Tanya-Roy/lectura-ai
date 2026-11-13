import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.database.models import JobStatus
from app.database.schemas import (
    CourseCreate,
    CourseDetailResponse,
    CourseResponse,
    CourseUpdate,
    VideoResponse,
)
from app.dependencies import PaginationParams, get_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])

# Mock database store for rapid Phase 1 testing and initial state
MOCK_COURSES: List[dict] = [
    {
        "id": "crs_ml_101",
        "user_id": "usr_demo_lectura_101",
        "title": "Machine Learning & Statistical Optimization",
        "description": "Foundational curriculum covering gradient descent, generalization bounds, regularization, and deep network architectures.",
        "channel_name": "MIT OpenCourseWare",
        "thumbnail_url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600&auto=format&fit=crop&q=80",
        "is_playlist": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "video_count": 8,
    },
    {
        "id": "crs_quantum_201",
        "user_id": "usr_demo_lectura_101",
        "title": "Quantum Mechanics & Hilbert Spaces",
        "description": "Rigorous undergraduate formulation of quantum states, wave equations, Hamiltonian operators, and perturbation theory.",
        "channel_name": "Stanford Physics",
        "thumbnail_url": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=600&auto=format&fit=crop&q=80",
        "is_playlist": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "video_count": 1,
    },
    {
        "id": "crs_neuro_301",
        "user_id": "usr_demo_lectura_101",
        "title": "Computational Neuroscience & Synaptic Plasticity",
        "description": "Mathematical models of neural firing, Hodgkin-Huxley equations, and spike-timing-dependent synaptic dynamics.",
        "channel_name": "Harvard Brain Initiative",
        "thumbnail_url": "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600&auto=format&fit=crop&q=80",
        "is_playlist": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "video_count": 5,
    },
]


@router.get("", response_model=List[CourseResponse])
async def list_courses(
    pagination: PaginationParams = Depends(),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[CourseResponse]:
    """Returns all courses associated with the current user."""
    return [CourseResponse(**c) for c in MOCK_COURSES]


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_in: CourseCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseResponse:
    """Creates a new course container."""
    new_course = {
        "id": f"crs_{uuid.uuid4().hex[:10]}",
        "user_id": current_user.id,
        "title": course_in.title,
        "description": course_in.description or "",
        "channel_name": course_in.channel_name or "Self-Directed",
        "thumbnail_url": course_in.thumbnail_url or "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600",
        "is_playlist": course_in.is_playlist,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "video_count": 0,
    }
    MOCK_COURSES.insert(0, new_course)
    return CourseResponse(**new_course)


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseDetailResponse:
    """Retrieves complete course details including video outline."""
    matching = next((c for c in MOCK_COURSES if c["id"] == course_id), None)
    if not matching:
        # Default mock detail if not in list
        matching = {
            "id": course_id,
            "user_id": current_user.id,
            "title": "Machine Learning & Statistical Optimization",
            "description": "Comprehensive course on deep learning, optimization algorithms, and statistical bounds.",
            "channel_name": "MIT OpenCourseWare",
            "thumbnail_url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600",
            "is_playlist": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "video_count": 3,
        }

    videos = [
        VideoResponse(
            id=f"vid_{course_id}_{i+1}",
            course_id=course_id,
            youtube_video_id=f"yt_vid_{i+1}",
            title=f"Lecture {i+1}: Foundations of Loss Minimization & Regularization",
            description="Exploration of convex loss spaces and gradient propagation.",
            duration_seconds=1200 + (i * 180),
            thumbnail_url="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
            channel_name=matching.get("channel_name", "Academic"),
            sequence_order=i + 1,
            processing_status=JobStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
        )
        for i in range(3)
    ]

    return CourseDetailResponse(
        **matching,
        videos=videos,
        playlists=[],
    )


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CourseResponse:
    """Updates course title or description."""
    matching = next((c for c in MOCK_COURSES if c["id"] == course_id), None)
    if not matching:
        raise HTTPException(status_code=404, detail="Course not found")

    if course_update.title:
        matching["title"] = course_update.title
    if course_update.description:
        matching["description"] = course_update.description
    matching["updated_at"] = datetime.now(timezone.utc)
    return CourseResponse(**matching)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a course and all associated notes."""
    global MOCK_COURSES
    MOCK_COURSES = [c for c in MOCK_COURSES if c["id"] != course_id]
    return None
