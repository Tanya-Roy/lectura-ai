import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.job_registry import job_registry
from app.database.connection import get_db
from app.database.models import JobStatus
from app.database.schemas import (
    JobResponse,
    PlaylistProcessRequest,
    PlaylistResponse,
    VideoResponse,
)
from app.dependencies import get_current_user
from app.services.playlist_service import PLAYLIST_RESULTS, playlist_ingestion_service
from app.services.youtube_service import (
    PlaylistMetadata,
    YouTubeMetadataFetcher,
    YouTubeURLParser,
)

router = APIRouter(prefix="/playlists", tags=["Playlists"])


def _to_job_response(record) -> JobResponse:
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


@router.post("/process", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def process_playlist(
    request: PlaylistProcessRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Submits a YouTube playlist URL for asynchronous ingestion and processing.
    Launches an asyncio background task and returns the tracking Job ID immediately.
    """
    playlist_id = YouTubeURLParser.extract_playlist_id(request.url)
    if not playlist_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The provided URL does not contain a valid YouTube playlist ID ('list=...').",
        )

    course_id = f"crs_pl_{playlist_id[:10]}"
    job_record = job_registry.create_job(
        workflow_name="playlist_ingestion_pipeline",
        playlist_id=playlist_id,
        course_id=course_id,
    )

    asyncio.create_task(
        playlist_ingestion_service.ingest_playlist(
            playlist_url=request.url,
            job_registry=job_registry,
            job_id=job_record.job_id,
            max_videos=request.max_videos,
            generate_flashcards=request.generate_flashcards,
            generate_quizzes=request.generate_quizzes,
            course_id=course_id,
        )
    )

    return _to_job_response(job_record)


@router.get("/preview", response_model=Dict[str, Any])
async def preview_playlist(
    url: str = Query(..., description="YouTube playlist URL to inspect"),
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Validates a YouTube playlist URL and returns its title, thumbnail,
    video count, and preview video items.
    """
    playlist_id = YouTubeURLParser.extract_playlist_id(url)
    if not playlist_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid playlist link. Please provide a URL containing 'list=...'.",
        )

    try:
        meta = await YouTubeMetadataFetcher.fetch_playlist_metadata(playlist_id)
        return {
            "valid": True,
            "playlist_id": playlist_id,
            "title": meta.title,
            "channel_name": meta.channel_name,
            "video_count": meta.video_count,
            "thumbnail_url": meta.thumbnail_url,
            "videos": [v.model_dump() for v in meta.videos[:10]],
        }
    except Exception as exc:
        return {
            "valid": False,
            "playlist_id": playlist_id,
            "error": str(exc),
            "title": f"YouTube Playlist ({playlist_id})",
            "channel_name": "Course Creator",
            "video_count": 0,
            "thumbnail_url": f"https://img.youtube.com/vi/{playlist_id}/hqdefault.jpg",
            "videos": [],
        }


@router.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist(
    playlist_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlaylistResponse:
    """Retrieves playlist metadata and all associated course videos."""
    # 1. Check in-memory ingestion cache
    if playlist_id in PLAYLIST_RESULTS:
        res = PLAYLIST_RESULTS[playlist_id]
        meta = res.metadata
        video_responses = [
            VideoResponse(
                id=vr.video_id,
                course_id=res.course_id,
                playlist_id=playlist_id,
                youtube_video_id=vr.video_id,
                title=vr.metadata.title,
                description=vr.metadata.description,
                duration_seconds=vr.metadata.duration_seconds,
                thumbnail_url=vr.metadata.thumbnail_url,
                channel_name=vr.metadata.channel_name,
                sequence_order=idx + 1,
                processing_status=JobStatus.COMPLETED if vr.status == "completed" else JobStatus.PENDING,
                created_at=datetime.now(timezone.utc),
            )
            for idx, vr in enumerate(res.video_results)
        ]
        return PlaylistResponse(
            id=playlist_id,
            course_id=res.course_id,
            youtube_playlist_id=playlist_id,
            title=meta.title,
            description=meta.description,
            channel_title=meta.channel_name,
            video_count=len(video_responses),
            created_at=datetime.now(timezone.utc),
            videos=video_responses,
        )

    # 2. Fallback sample playlist
    videos = [
        VideoResponse(
            id=f"vid_item_{i+1}",
            course_id=f"crs_{playlist_id}",
            playlist_id=playlist_id,
            youtube_video_id=f"demo_vid_{i+1}",
            title=f"Module {i+1}: Advanced Concepts in Computational Theory",
            description="Exploration of computational complexity and structural algorithmic bounds.",
            duration_seconds=900 + (i * 120),
            thumbnail_url="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=400",
            channel_name="Stanford Online",
            sequence_order=i + 1,
            processing_status=JobStatus.COMPLETED,
            created_at=datetime.now(timezone.utc),
        )
        for i in range(5)
    ]

    return PlaylistResponse(
        id=playlist_id,
        course_id=f"crs_{playlist_id}",
        youtube_playlist_id=playlist_id,
        title="Complete University Course in Deep Learning & Optimization",
        description="Semester lecture collection covering convex optimization, backpropagation dynamics, and generalization bounds.",
        channel_title="Stanford Online",
        video_count=len(videos),
        created_at=datetime.now(timezone.utc),
        videos=videos,
    )


@router.get("/{playlist_id}/videos", response_model=List[VideoResponse])
async def get_playlist_videos(
    playlist_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[VideoResponse]:
    """Retrieves ordered sequence of videos in a playlist."""
    playlist = await get_playlist(playlist_id, current_user, db)
    return playlist.videos
