"""
Playlist Ingestion Service — Phase 2 Implementation

Orchestrates sequential or batch ingestion of entire YouTube playlists:
1. Playlist URL parsing and validation
2. Retrieval of playlist metadata and ordered video items
3. Child video ingestion orchestration
4. In-memory storage of playlist results
"""

import time
import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.exceptions import VideoProcessingError
from app.core.job_registry import JobRegistry, job_registry as default_job_registry
from app.core.logging import logger
from app.services.transcript_service import (
    INGESTION_RESULTS,
    IngestionResult,
    VideoIngestionService,
    video_ingestion_service,
)
from app.services.youtube_service import (
    PlaylistMetadata,
    PlaylistVideoItem,
    YouTubeMetadataFetcher,
    YouTubeURLParser,
)


class PlaylistIngestionResult(BaseModel):
    job_id: str
    playlist_id: str
    course_id: str
    metadata: PlaylistMetadata
    video_results: List[IngestionResult] = Field(default_factory=list)
    status: str = "completed"  # "completed" | "partial" | "failed"
    warnings: List[str] = Field(default_factory=list)
    total_videos: int = 0
    completed_videos: int = 0
    processing_time_seconds: float = 0.0


# In-memory storage for playlist ingestion results
PLAYLIST_RESULTS: Dict[str, PlaylistIngestionResult] = {}
JOB_PLAYLIST_MAP: Dict[str, PlaylistIngestionResult] = {}


class PlaylistIngestionService:
    """Handles playlist-level ingestion and child video coordination."""

    def __init__(self) -> None:
        self.url_parser = YouTubeURLParser()
        self.metadata_fetcher = YouTubeMetadataFetcher()
        self.video_service = video_ingestion_service

    async def ingest_playlist(
        self,
        playlist_url: str,
        job_registry: Optional[JobRegistry] = None,
        job_id: Optional[str] = None,
        max_videos: int = 50,
        generate_flashcards: bool = True,
        generate_quizzes: bool = True,
        course_id: Optional[str] = None,
    ) -> PlaylistIngestionResult:
        """
        Orchestrates full playlist ingestion with per-video processing updates.
        """
        start_time = time.time()
        registry = job_registry or default_job_registry

        if not job_id:
            job_record = registry.create_job(
                workflow_name="playlist_ingestion_pipeline",
                course_id=course_id,
            )
            job_id = job_record.job_id

        warnings: List[str] = []
        video_results: List[IngestionResult] = []

        try:
            # 1. URL extraction
            registry.update_progress(
                job_id,
                node="playlist_validation",
                message=f"Parsing playlist URL: {playlist_url}",
                progress=10,
            )

            playlist_id = self.url_parser.extract_playlist_id(playlist_url)
            if not playlist_id:
                raise VideoProcessingError(
                    f"No playlist ID ('list=') could be found in '{playlist_url}'."
                )

            job_rec = registry.get_job(job_id)
            if job_rec:
                job_rec.playlist_id = playlist_id

            # 2. Fetch Playlist Metadata
            registry.update_progress(
                job_id,
                node="playlist_metadata",
                message=f"Fetching playlist metadata for '{playlist_id}'...",
                progress=20,
            )

            metadata = await self.metadata_fetcher.fetch_playlist_metadata(playlist_id)
            effective_course_id = course_id or f"crs_pl_{playlist_id[:10]}"

            videos_to_process = metadata.videos[:max_videos]
            total_target = len(videos_to_process)

            registry.update_progress(
                job_id,
                node="playlist_metadata",
                message=f"Playlist '{metadata.title}': found {len(metadata.videos)} videos, processing {total_target}",
                progress=25,
            )

            # 3. Process Individual Videos
            completed_count = 0
            for idx, video_item in enumerate(videos_to_process):
                video_url = f"https://www.youtube.com/watch?v={video_item.video_id}"
                current_percent = int(25 + ((idx / max(total_target, 1)) * 65))

                registry.update_progress(
                    job_id,
                    node="video_ingestion",
                    message=f"Processing video {idx + 1}/{total_target}: {video_item.title}",
                    progress=current_percent,
                )

                try:
                    # Ingest child video
                    child_job_id = f"{job_id}_vid_{video_item.video_id}"
                    vid_result = await self.video_service.ingest_video(
                        url=video_url,
                        job_registry=registry,
                        job_id=child_job_id,
                        course_id=effective_course_id,
                        generate_flashcards=generate_flashcards,
                        generate_quizzes=generate_quizzes,
                    )
                    video_results.append(vid_result)
                    completed_count += 1
                except Exception as child_exc:
                    logger.warning(
                        f"Failed ingesting playlist video {video_item.video_id}: {child_exc}"
                    )
                    warnings.append(
                        f"Video {video_item.video_id} ('{video_item.title}') failed: {child_exc}"
                    )

            # 4. Finalize
            processing_time = round(time.time() - start_time, 2)
            playlist_status = (
                "completed"
                if completed_count == total_target and total_target > 0
                else ("partial" if completed_count > 0 else "failed")
            )

            result = PlaylistIngestionResult(
                job_id=job_id,
                playlist_id=playlist_id,
                course_id=effective_course_id,
                metadata=metadata,
                video_results=video_results,
                status=playlist_status,
                warnings=warnings,
                total_videos=total_target,
                completed_videos=completed_count,
                processing_time_seconds=processing_time,
            )

            PLAYLIST_RESULTS[playlist_id] = result
            JOB_PLAYLIST_MAP[job_id] = result

            registry.complete_job(
                job_id,
                message=f"Playlist processing completed in {processing_time}s ({completed_count}/{total_target} videos ingested)",
                result=result,
            )
            return result

        except Exception as exc:
            logger.error(f"Playlist ingestion failure for {playlist_url}: {exc}")
            registry.fail_job(job_id, error=str(exc))
            raise


# Global singleton instance
playlist_ingestion_service = PlaylistIngestionService()
