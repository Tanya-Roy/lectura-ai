"""
Video Ingestion Service — Phase 2 Implementation

Orchestrates the complete single-video ingestion pipeline:
1. URL parsing & ID extraction
2. Rich metadata extraction (oEmbed + Data API v3)
3. Subtitle / transcript extraction (API + fallbacks)
4. Normalization and audio artifact removal
5. Intelligent topic-boundary chunking
6. Job registry real-time progress logging
7. In-memory result cache
"""

import time
import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.exceptions import VideoProcessingError
from app.core.job_registry import JobRegistry, job_registry as default_job_registry
from app.core.logging import logger
from app.services.youtube_service import (
    TopicBoundaryChunker,
    TranscriptChunk,
    TranscriptExtractor,
    TranscriptNormalizer,
    TranscriptResult,
    TranscriptSegment,
    VideoMetadata,
    YouTubeMetadataFetcher,
    YouTubeURLParser,
)


class IngestionResult(BaseModel):
    job_id: str
    video_id: str
    course_id: str
    metadata: VideoMetadata
    transcript: TranscriptResult
    chunks: List[TranscriptChunk] = Field(default_factory=list)
    status: str = "completed"  # "completed" | "partial" | "failed"
    warnings: List[str] = Field(default_factory=list)
    processing_time_seconds: float = 0.0


# In-memory storage for ingested video results (persists during backend runtime)
INGESTION_RESULTS: Dict[str, IngestionResult] = {}
JOB_INGESTION_MAP: Dict[str, IngestionResult] = {}


class VideoIngestionService:
    """Orchestrates the complete video ingestion pipeline."""

    def __init__(self) -> None:
        self.url_parser = YouTubeURLParser()
        self.metadata_fetcher = YouTubeMetadataFetcher()
        self.transcript_extractor = TranscriptExtractor()
        self.normalizer = TranscriptNormalizer()
        self.chunker = TopicBoundaryChunker()

    async def ingest_video(
        self,
        url: str,
        job_registry: Optional[JobRegistry] = None,
        job_id: Optional[str] = None,
        course_id: Optional[str] = None,
        generate_flashcards: bool = True,
        generate_quizzes: bool = True,
    ) -> IngestionResult:
        """
        Executes end-to-end ingestion pipeline with granular progress reporting.
        """
        start_time = time.time()
        registry = job_registry or default_job_registry

        # Ensure a job record exists in registry
        if not job_id:
            job_record = registry.create_job(
                workflow_name="video_ingestion_pipeline",
                course_id=course_id,
            )
            job_id = job_record.job_id

        warnings: List[str] = []

        try:
            # 1. URL Parsing & Validation
            registry.update_progress(
                job_id,
                node="url_validation",
                message=f"Validating YouTube URL: {url}",
                progress=10,
            )

            video_id = self.url_parser.extract_video_id(url)
            if not video_id:
                raise VideoProcessingError(
                    f"Could not extract a valid 11-character YouTube video ID from '{url}'."
                )

            # Update job record with extracted video_id
            job_rec = registry.get_job(job_id)
            if job_rec:
                job_rec.video_id = video_id

            registry.update_progress(
                job_id,
                node="url_validation",
                message=f"Successfully validated video ID: {video_id}",
                progress=20,
            )

            # 2. Fetch Video Metadata
            registry.update_progress(
                job_id,
                node="metadata_fetch",
                message="Fetching video title, author, and thumbnail...",
                progress=35,
            )
            metadata = await self.metadata_fetcher.fetch_video_metadata(video_id)
            registry.update_progress(
                job_id,
                node="metadata_fetch",
                message=f"Retrieved: '{metadata.title}' ({metadata.channel_name})",
                progress=50,
            )

            # 3. Extract Transcript
            registry.update_progress(
                job_id,
                node="transcript_extraction",
                message="Retrieving transcript subtitles via YouTube API...",
                progress=65,
            )
            transcript_result = self.transcript_extractor.extract(video_id)
            if transcript_result.warnings:
                warnings.extend(transcript_result.warnings)
                for w in transcript_result.warnings:
                    registry.update_progress(
                        job_id,
                        node="transcript_extraction",
                        message=f"Warning: {w}",
                        progress=70,
                        level="warning",
                    )

            # 4. Normalize & Clean Transcript Segments
            normalized_segments: List[TranscriptSegment] = []
            if transcript_result.segments:
                registry.update_progress(
                    job_id,
                    node="normalization",
                    message="Normalizing transcript and removing filler noise...",
                    progress=75,
                )
                cleaned = self.normalizer.normalize(transcript_result.segments)
                normalized_segments = self.normalizer.merge_short_segments(cleaned, min_duration=2.0)
                transcript_result.segments = normalized_segments
                transcript_result.raw_text = " ".join(s.text for s in normalized_segments)

            # 5. Intelligent Topic Boundary Chunking
            chunks: List[TranscriptChunk] = []
            if normalized_segments:
                registry.update_progress(
                    job_id,
                    node="topic_chunking",
                    message="Analyzing lecture transitions and computing topic boundaries...",
                    progress=85,
                )
                chunks = self.chunker.chunk(
                    normalized_segments,
                    target_chunk_seconds=120.0,
                    max_chunk_seconds=300.0,
                )
                transcript_result.chunk_count = len(chunks)
                registry.update_progress(
                    job_id,
                    node="topic_chunking",
                    message=f"Synthesized {len(chunks)} topic-boundary lecture chunks",
                    progress=95,
                )
            else:
                warnings.append("No transcript segments could be extracted for chunking.")

            # 6. Complete Ingestion
            processing_time = round(time.time() - start_time, 2)
            ingestion_status = "completed" if chunks else ("partial" if transcript_result.segments else "failed")
            effective_course_id = course_id or f"crs_{video_id[:8]}"

            result = IngestionResult(
                job_id=job_id,
                video_id=video_id,
                course_id=effective_course_id,
                metadata=metadata,
                transcript=transcript_result,
                chunks=chunks,
                status=ingestion_status,
                warnings=warnings,
                processing_time_seconds=processing_time,
            )

            # Store in caches
            INGESTION_RESULTS[video_id] = result
            JOB_INGESTION_MAP[job_id] = result

            registry.complete_job(
                job_id,
                message=f"Ingestion finished in {processing_time}s ({len(chunks)} chunks ready)",
                result=result,
            )
            return result

        except Exception as exc:
            logger.error(f"Video ingestion pipeline failure for {url}: {exc}")
            registry.fail_job(job_id, error=str(exc))
            raise


# Global singleton instance
video_ingestion_service = VideoIngestionService()
