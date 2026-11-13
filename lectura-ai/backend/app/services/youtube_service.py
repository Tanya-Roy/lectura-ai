"""
YouTube Service — Phase 2 Complete Implementation

Handles:
- URL validation (video + playlist formats)
- Video metadata via oEmbed (no API key required) + YouTube Data API v3 (if key set)
- Playlist enumeration via YouTube Data API v3 (with fallback)
- Transcript extraction via youtube-transcript-api
- SRT/VTT/TXT transcript parsing
- Intelligent chunking by topic boundaries
- Transcript normalization and cleaning
"""

import html
import re
import uuid
from typing import Any, Dict, List, Literal, Optional, Tuple
import httpx
from pydantic import BaseModel, Field
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    CouldNotRetrieveTranscript,
)

from app.config import settings
from app.core.exceptions import VideoProcessingError
from app.core.logging import logger


# ==========================================
# Pydantic Models
# ==========================================


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class TranscriptChunk(BaseModel):
    chunk_id: str
    chunk_index: int
    start_time: float
    end_time: float
    text: str
    topic_hint: Optional[str] = None
    preceding_context: str = ""
    word_count: int = 0


class TranscriptResult(BaseModel):
    video_id: str
    language: str = "en"
    is_auto_generated: bool = False
    extraction_method: str = "unavailable"  # "youtube_captions" | "auto_generated" | "unavailable"
    segments: List[TranscriptSegment] = Field(default_factory=list)
    raw_text: str = ""
    warnings: List[str] = Field(default_factory=list)
    chunk_count: int = 0


class VideoMetadata(BaseModel):
    video_id: str
    title: str
    channel_name: str
    channel_url: str = ""
    thumbnail_url: str
    duration_seconds: int = 600
    description: str = ""


class PlaylistVideoItem(BaseModel):
    video_id: str
    title: str
    thumbnail_url: str
    position: int
    channel_name: str = ""


class PlaylistMetadata(BaseModel):
    playlist_id: str
    title: str
    channel_name: str
    description: str = ""
    video_count: int = 0
    thumbnail_url: str = ""
    videos: List[PlaylistVideoItem] = Field(default_factory=list)


# ==========================================
# YouTube URL Parser
# ==========================================


class YouTubeURLParser:
    """Parses and validates YouTube video and playlist URLs."""

    # Video URL patterns: watch?v=, youtu.be/, embed/, shorts/, live/, v/
    VIDEO_PATTERNS = [
        re.compile(r"(?:https?:\/\/)?(?:www\.|m\.)?youtube\.com\/watch\?(?:.*&)?v=([a-zA-Z0-9_-]{11})", re.IGNORECASE),
        re.compile(r"(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})", re.IGNORECASE),
        re.compile(r"(?:https?:\/\/)?(?:www\.|m\.)?youtube\.com\/(?:embed|shorts|live|v)\/([a-zA-Z0-9_-]{11})", re.IGNORECASE),
    ]

    PLAYLIST_PATTERN = re.compile(r"[?&]list=([a-zA-Z0-9_-]+)", re.IGNORECASE)

    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """Extracts the 11-character video ID from any standard YouTube URL."""
        if not url:
            return None
        cleaned = url.strip()
        for pattern in cls.VIDEO_PATTERNS:
            match = pattern.search(cleaned)
            if match:
                return match.group(1)
        return None

    @classmethod
    def extract_playlist_id(cls, url: str) -> Optional[str]:
        """Extracts the playlist ID from a YouTube playlist or video-in-playlist URL."""
        if not url:
            return None
        cleaned = url.strip()
        match = cls.PLAYLIST_PATTERN.search(cleaned)
        if match:
            return match.group(1)
        return None

    @classmethod
    def classify_url(cls, url: str) -> Literal["video", "playlist", "video_in_playlist", "invalid"]:
        """Classifies the URL format into video, playlist, video_in_playlist, or invalid."""
        if not url:
            return "invalid"
        cleaned = url.strip()

        # Quick domain sanity check
        if not any(domain in cleaned.lower() for domain in ["youtube.com", "youtu.be"]):
            return "invalid"

        video_id = cls.extract_video_id(cleaned)
        playlist_id = cls.extract_playlist_id(cleaned)

        if video_id and playlist_id:
            return "video_in_playlist"
        elif playlist_id:
            return "playlist"
        elif video_id:
            return "video"
        return "invalid"

    @classmethod
    def is_valid_youtube_url(cls, url: str) -> bool:
        """Returns True if the URL is a recognized YouTube video or playlist format."""
        return cls.classify_url(url) != "invalid"


# ==========================================
# YouTube Metadata Fetcher
# ==========================================


def _parse_iso8601_duration(duration_str: str) -> int:
    """Parses ISO 8601 duration (e.g., PT1H2M30S) into total seconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not match:
        return 600
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


class YouTubeMetadataFetcher:
    """
    Fetches rich video and playlist metadata.
    Uses oEmbed for fast, API-key-free video metadata with fallback to Data API v3.
    """

    @classmethod
    async def fetch_video_metadata(cls, video_id: str) -> VideoMetadata:
        """
        Fetches video metadata via YouTube Data API v3 if key available,
        otherwise falls back to YouTube oEmbed service.
        """
        # If API key is configured, attempt Data API v3 for full description & duration
        if settings.YOUTUBE_API_KEY:
            try:
                api_url = "https://www.googleapis.com/youtube/v3/videos"
                params = {
                    "part": "snippet,contentDetails",
                    "id": video_id,
                    "key": settings.YOUTUBE_API_KEY,
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(api_url, params=params)
                    if resp.status_code == 200:
                        items = resp.json().get("items", [])
                        if items:
                            item = items[0]
                            snippet = item.get("snippet", {})
                            content_details = item.get("contentDetails", {})
                            thumbnails = snippet.get("thumbnails", {})
                            thumb_url = (
                                thumbnails.get("maxres", {}).get("url")
                                or thumbnails.get("high", {}).get("url")
                                or thumbnails.get("medium", {}).get("url")
                                or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                            )
                            duration_secs = _parse_iso8601_duration(content_details.get("duration", "PT10M"))
                            return VideoMetadata(
                                video_id=video_id,
                                title=snippet.get("title", f"YouTube Video ({video_id})"),
                                channel_name=snippet.get("channelTitle", "YouTube Creator"),
                                channel_url=f"https://www.youtube.com/channel/{snippet.get('channelId', '')}",
                                thumbnail_url=thumb_url,
                                duration_seconds=duration_secs,
                                description=snippet.get("description", ""),
                            )
            except Exception as exc:
                logger.warning(f"YouTube Data API v3 fetch failed for {video_id}: {exc}. Trying oEmbed.")

        # oEmbed fallback (No API key needed)
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(oembed_url)
                if resp.status_code == 200:
                    data = resp.json()
                    return VideoMetadata(
                        video_id=video_id,
                        title=data.get("title", f"YouTube Video ({video_id})"),
                        channel_name=data.get("author_name", "YouTube Creator"),
                        channel_url=data.get("author_url", f"https://www.youtube.com/watch?v={video_id}"),
                        thumbnail_url=data.get("thumbnail_url", f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"),
                        duration_seconds=600,
                        description=f"Educational lecture by {data.get('author_name', 'YouTube Creator')}.",
                    )
                elif resp.status_code == 404:
                    raise VideoProcessingError(
                        f"This YouTube video could not be found. Check the URL.",
                        details={"video_id": video_id, "status_code": 404},
                    )
        except VideoProcessingError:
            raise
        except Exception as exc:
            logger.warning(f"Failed to fetch oEmbed metadata for {video_id}: {exc}")

        # Final resilient default
        return VideoMetadata(
            video_id=video_id,
            title=f"YouTube Video ({video_id})",
            channel_name="YouTube Creator",
            channel_url=f"https://www.youtube.com/watch?v={video_id}",
            thumbnail_url=f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
            duration_seconds=600,
            description="Video metadata unavailable via public endpoints.",
        )

    @classmethod
    async def fetch_playlist_metadata(cls, playlist_id: str) -> PlaylistMetadata:
        """
        Fetches playlist details and enclosed videos via YouTube Data API v3.
        Requires YOUTUBE_API_KEY.
        """
        if not settings.YOUTUBE_API_KEY:
            raise VideoProcessingError(
                "YouTube API key is needed to list playlist videos. Add YOUTUBE_API_KEY to your .env file."
            )

        api_url = "https://www.googleapis.com/youtube/v3/playlists"
        params = {
            "part": "snippet,contentDetails",
            "id": playlist_id,
            "key": settings.YOUTUBE_API_KEY,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(api_url, params=params)
            if resp.status_code != 200:
                raise VideoProcessingError(
                    f"Failed to query playlist from YouTube Data API (status {resp.status_code})."
                )
            items = resp.json().get("items", [])
            if not items:
                raise VideoProcessingError(f"Playlist with ID '{playlist_id}' not found.")

            snippet = items[0].get("snippet", {})
            content_details = items[0].get("contentDetails", {})
            thumbnails = snippet.get("thumbnails", {})
            thumb_url = (
                thumbnails.get("maxres", {}).get("url")
                or thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or f"https://img.youtube.com/vi/{playlist_id}/hqdefault.jpg"
            )

            videos = await cls.fetch_playlist_videos(playlist_id)

            return PlaylistMetadata(
                playlist_id=playlist_id,
                title=snippet.get("title", f"Playlist {playlist_id}"),
                channel_name=snippet.get("channelTitle", "Course Creator"),
                description=snippet.get("description", ""),
                video_count=content_details.get("itemCount", len(videos)),
                thumbnail_url=thumb_url,
                videos=videos,
            )

    @classmethod
    async def fetch_playlist_videos(cls, playlist_id: str, max_results: int = 50) -> List[PlaylistVideoItem]:
        """Paginates through playlistItems using nextPageToken."""
        if not settings.YOUTUBE_API_KEY:
            return []

        api_url = "https://www.googleapis.com/youtube/v3/playlistItems"
        videos: List[PlaylistVideoItem] = []
        next_page_token: Optional[str] = None

        async with httpx.AsyncClient(timeout=15.0) as client:
            while len(videos) < max_results:
                params: Dict[str, Any] = {
                    "part": "snippet",
                    "playlistId": playlist_id,
                    "maxResults": min(50, max_results - len(videos)),
                    "key": settings.YOUTUBE_API_KEY,
                }
                if next_page_token:
                    params["pageToken"] = next_page_token

                resp = await client.get(api_url, params=params)
                if resp.status_code != 200:
                    break

                data = resp.json()
                items = data.get("items", [])
                if not items:
                    break

                for item in items:
                    snip = item.get("snippet", {})
                    v_id = snip.get("resourceId", {}).get("videoId")
                    v_title = snip.get("title", "")
                    if not v_id or v_title in ["Private video", "Deleted video"]:
                        continue

                    thumbs = snip.get("thumbnails", {})
                    t_url = (
                        thumbs.get("high", {}).get("url")
                        or thumbs.get("medium", {}).get("url")
                        or thumbs.get("default", {}).get("url")
                        or f"https://img.youtube.com/vi/{v_id}/hqdefault.jpg"
                    )

                    videos.append(
                        PlaylistVideoItem(
                            video_id=v_id,
                            title=v_title,
                            thumbnail_url=t_url,
                            position=snip.get("position", len(videos) + 1),
                            channel_name=snip.get("videoOwnerChannelTitle", snip.get("channelTitle", "")),
                        )
                    )

                next_page_token = data.get("nextPageToken")
                if not next_page_token:
                    break

        return videos


# ==========================================
# Transcript Extractor
# ==========================================


class TranscriptExtractor:
    """Extracts YouTube transcripts via API or parses uploaded subtitle files (SRT, VTT, TXT)."""

    def extract(self, video_id: str, preferred_languages: Optional[List[str]] = None) -> TranscriptResult:
        """
        Attempts extraction via youtube-transcript-api.
        Handles disabled transcripts, auto-generated transcripts, and rate-limiting gracefully.
        """
        languages = preferred_languages or ["en", "en-US", "en-GB", "es", "fr", "de"]

        try:
            # 1. Inspect transcript listings for manual captions first, then auto-generated
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            selected_transcript = None
            is_auto = False

            try:
                # Prefer manually created transcript
                selected_transcript = transcript_list.find_manually_created_transcript(languages)
                is_auto = False
            except Exception:
                try:
                    # Fallback to generated transcript
                    selected_transcript = transcript_list.find_generated_transcript(languages)
                    is_auto = True
                except Exception:
                    # Fallback to any transcript available
                    for t in transcript_list:
                        selected_transcript = t
                        is_auto = t.is_generated
                        break

            if not selected_transcript:
                return TranscriptResult(
                    video_id=video_id,
                    extraction_method="unavailable",
                    warnings=["No transcript was found for this video in your preferred languages."],
                )

            raw_items = selected_transcript.fetch()
            segments = [
                TranscriptSegment(
                    start=round(float(item["start"]), 2),
                    end=round(float(item["start"]) + float(item.get("duration", 0.0)), 2),
                    text=html.unescape(item["text"]).strip(),
                )
                for item in raw_items
                if item.get("text", "").strip()
            ]

            raw_text = " ".join(s.text for s in segments)
            warnings = ["Using auto-generated captions, accuracy may vary"] if is_auto else []
            method = "auto_generated" if is_auto else "youtube_captions"

            return TranscriptResult(
                video_id=video_id,
                language=selected_transcript.language_code,
                is_auto_generated=is_auto,
                extraction_method=method,
                segments=segments,
                raw_text=raw_text,
                warnings=warnings,
                chunk_count=0,
            )

        except TranscriptsDisabled:
            return TranscriptResult(
                video_id=video_id,
                extraction_method="unavailable",
                warnings=["Captions are disabled for this video. Please upload a transcript file."],
            )
        except NoTranscriptFound:
            return TranscriptResult(
                video_id=video_id,
                extraction_method="unavailable",
                warnings=["No transcript was found for this video in your preferred languages."],
            )
        except CouldNotRetrieveTranscript:
            return TranscriptResult(
                video_id=video_id,
                extraction_method="unavailable",
                warnings=["Could not retrieve the transcript. YouTube may be rate-limiting — try again in a moment."],
            )
        except Exception as exc:
            logger.warning(f"Unexpected error extracting transcript for {video_id}: {exc}")
            return TranscriptResult(
                video_id=video_id,
                extraction_method="unavailable",
                warnings=[f"Could not retrieve transcript: {str(exc)}"],
            )

    @classmethod
    def _parse_timestamp(cls, ts_str: str) -> float:
        """Parses HH:MM:SS,mmm or HH:MM:SS.mmm or MM:SS.mmm into seconds float."""
        clean = ts_str.strip().replace(",", ".")
        parts = clean.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return float(h) * 3600 + float(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return float(m) * 60 + float(s)
        return float(clean)

    @classmethod
    def _strip_html(cls, text: str) -> str:
        """Removes HTML markup commonly found in subtitles like <i>, <b>, <font>."""
        return re.sub(r"<[^>]+>", "", text)

    def parse_srt(self, content: str) -> List[TranscriptSegment]:
        """Parses standard SubRip (.srt) subtitle format."""
        segments: List[TranscriptSegment] = []
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        blocks = re.split(r"\n\s*\n", normalized.strip())

        time_pattern = re.compile(
            r"(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3})"
        )

        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue

            # Find the line with the timestamp arrow
            time_idx = -1
            time_match = None
            for idx, line in enumerate(lines):
                match = time_pattern.search(line)
                if match:
                    time_idx = idx
                    time_match = match
                    break

            if time_match and time_idx != -1:
                start_sec = self._parse_timestamp(time_match.group(1))
                end_sec = self._parse_timestamp(time_match.group(2))
                text_lines = lines[time_idx + 1 :]
                text = " ".join(self._strip_html(tl) for tl in text_lines).strip()
                if text:
                    segments.append(
                        TranscriptSegment(
                            start=round(start_sec, 2),
                            end=round(end_sec, 2),
                            text=html.unescape(text),
                        )
                    )

        return segments

    def parse_vtt(self, content: str) -> List[TranscriptSegment]:
        """Parses WebVTT (.vtt) subtitle format."""
        segments: List[TranscriptSegment] = []
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        # Remove WEBVTT header and NOTE blocks
        clean_content = re.sub(r"^WEBVTT.*?\n\n", "", normalized, flags=re.DOTALL | re.IGNORECASE)
        blocks = re.split(r"\n\s*\n", clean_content.strip())

        time_pattern = re.compile(
            r"((?:\d{1,2}:)?\d{2}:\d{2}[\.]\d{1,3})\s*-->\s*((?:\d{1,2}:)?\d{2}:\d{2}[\.]\d{1,3})"
        )

        for block in blocks:
            if block.strip().startswith("NOTE"):
                continue

            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue

            time_idx = -1
            time_match = None
            for idx, line in enumerate(lines):
                match = time_pattern.search(line)
                if match:
                    time_idx = idx
                    time_match = match
                    break

            if time_match and time_idx != -1:
                start_sec = self._parse_timestamp(time_match.group(1))
                end_sec = self._parse_timestamp(time_match.group(2))
                text_lines = lines[time_idx + 1 :]
                text = " ".join(self._strip_html(tl) for tl in text_lines).strip()
                if text:
                    segments.append(
                        TranscriptSegment(
                            start=round(start_sec, 2),
                            end=round(end_sec, 2),
                            text=html.unescape(text),
                        )
                    )

        return segments

    def parse_txt(self, content: str) -> List[TranscriptSegment]:
        """Parses raw text transcript as contiguous semantic blocks."""
        cleaned = content.strip()
        if not cleaned:
            return []
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", cleaned) if p.strip()]
        if not paragraphs:
            return [TranscriptSegment(start=0.0, end=0.0, text=cleaned)]

        segments: List[TranscriptSegment] = []
        # Estimate ~30 seconds per paragraph if no timestamps present
        est_duration = 30.0
        for i, para in enumerate(paragraphs):
            segments.append(
                TranscriptSegment(
                    start=round(i * est_duration, 2),
                    end=round((i + 1) * est_duration, 2),
                    text=html.unescape(para),
                )
            )
        return segments


# ==========================================
# Transcript Normalizer
# ==========================================


class TranscriptNormalizer:
    """Cleans fillers, audio event markers, and merges brief fractured segments."""

    FILLER_PATTERN = re.compile(
        r"\[(music|applause|laughter|silence|foreign|cheering|chuckle|snicker)\]|\((music|applause|laughter|silence|foreign|cheering)\)",
        re.IGNORECASE,
    )

    @classmethod
    def normalize(cls, segments: List[TranscriptSegment]) -> List[TranscriptSegment]:
        """Cleans filler words, excessive spaces, and OCR/caption encoding artifacts."""
        cleaned_segments: List[TranscriptSegment] = []

        for seg in segments:
            # Strip sound cues
            text = cls.FILLER_PATTERN.sub("", seg.text)
            # Unescape html entities
            text = html.unescape(text)
            # Collapse multiple whitespaces
            text = re.sub(r"\s+", " ", text).strip()

            if text:
                cleaned_segments.append(
                    TranscriptSegment(
                        start=seg.start,
                        end=seg.end,
                        text=text,
                    )
                )

        return cleaned_segments

    @classmethod
    def merge_short_segments(
        cls, segments: List[TranscriptSegment], min_duration: float = 2.0
    ) -> List[TranscriptSegment]:
        """Merges segments shorter than min_duration with contiguous segments to prevent fragmentation."""
        if not segments:
            return []

        merged: List[TranscriptSegment] = []
        accumulator_text: List[str] = []
        acc_start = segments[0].start
        acc_end = segments[0].end

        for seg in segments:
            if not accumulator_text:
                acc_start = seg.start
                acc_end = seg.end
                accumulator_text.append(seg.text)
                continue

            # If current accumulated duration is still too short, merge
            if (acc_end - acc_start) < min_duration:
                accumulator_text.append(seg.text)
                acc_end = max(acc_end, seg.end)
            else:
                merged.append(
                    TranscriptSegment(
                        start=acc_start,
                        end=acc_end,
                        text=" ".join(accumulator_text),
                    )
                )
                acc_start = seg.start
                acc_end = seg.end
                accumulator_text = [seg.text]

        if accumulator_text:
            merged.append(
                TranscriptSegment(
                    start=acc_start,
                    end=acc_end,
                    text=" ".join(accumulator_text),
                )
            )

        return merged


# ==========================================
# Topic Boundary Chunker
# ==========================================


class TopicBoundaryChunker:
    """
    Intelligent chunking based on semantic lecture transitions, natural pause gaps,
    and sentence endings rather than naive fixed token lengths.
    """

    TRANSITION_PHRASES = [
        "now let's",
        "so let's",
        "moving on",
        "next we",
        "let me now",
        "in the next section",
        "okay so",
        "alright so",
        "let's talk about",
        "the next topic",
        "another concept",
        "in summary",
        "to summarize",
        "so to recap",
        "before we move on",
        "next topic",
        "turn our attention to",
    ]

    SENTENCE_ENDINGS = re.compile(r"[\.!?]\s*$")

    @classmethod
    def _detect_topic_hint(cls, text: str) -> Optional[str]:
        """Detects if any lecture transition phrase indicates the topic of the chunk."""
        lower = text.lower()
        for phrase in cls.TRANSITION_PHRASES:
            if phrase in lower:
                idx = lower.find(phrase)
                snippet = text[idx : idx + 60].strip()
                # Clean up punctuation
                return snippet.split(".")[0].strip()
        return None

    @classmethod
    def _get_last_sentences(cls, text: str, count: int = 2) -> str:
        """Extracts the last N sentences from text to carry over as preceding context."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return " ".join(sentences[-count:]) if sentences else ""

    def chunk(
        self,
        segments: List[TranscriptSegment],
        target_chunk_seconds: float = 120.0,
        max_chunk_seconds: float = 300.0,
        overlap_seconds: float = 10.0,
    ) -> List[TranscriptChunk]:
        """
        Chunks transcript segments using semantic transitions, pause boundaries (>3s),
        and natural sentence ends. Respects max_chunk_seconds hard ceiling and 30s minimum.
        """
        if not segments:
            return []

        chunks: List[TranscriptChunk] = []
        current_texts: List[str] = []
        chunk_start: float = segments[0].start
        last_seg_end: float = segments[0].end
        prev_chunk_text = ""
        chunk_idx = 0

        for i, seg in enumerate(segments):
            current_texts.append(seg.text)
            current_duration = seg.end - chunk_start
            last_seg_end = seg.end

            is_last = i == len(segments) - 1
            if is_last:
                break

            next_seg = segments[i + 1]
            silence_gap = next_seg.start - seg.end
            has_long_gap = silence_gap >= 3.0

            # Check if next segment begins with a lecture transition phrase
            next_text_lower = next_seg.text.lower().strip()
            starts_transition = any(
                next_text_lower.startswith(phrase) or f" {phrase}" in next_text_lower[:25]
                for phrase in self.TRANSITION_PHRASES
            )

            current_full_text = " ".join(current_texts)
            ends_sentence = bool(self.SENTENCE_ENDINGS.search(seg.text.strip()))

            # Topic boundary trigger conditions:
            # 1. Past minimum 30 seconds AND (silence gap OR (transition phrase preceded by sentence ending))
            # 2. Past target duration (120s) AND ends sentence
            # 3. Exceeded max duration (300s) hard ceiling
            should_split = False

            if current_duration >= 30.0 and (has_long_gap or (starts_transition and ends_sentence)):
                should_split = True
            elif current_duration >= target_chunk_seconds and ends_sentence:
                should_split = True
            elif current_duration >= max_chunk_seconds:
                should_split = True

            if should_split:
                chunk_text = " ".join(current_texts).strip()
                chunks.append(
                    TranscriptChunk(
                        chunk_id=f"chk_{uuid.uuid4().hex[:10]}",
                        chunk_index=chunk_idx,
                        start_time=round(chunk_start, 2),
                        end_time=round(last_seg_end, 2),
                        text=chunk_text,
                        topic_hint=self._detect_topic_hint(chunk_text),
                        preceding_context=self._get_last_sentences(prev_chunk_text, 2),
                        word_count=len(chunk_text.split()),
                    )
                )
                prev_chunk_text = chunk_text
                chunk_idx += 1
                current_texts = []
                chunk_start = next_seg.start

        # Final trailing chunk
        if current_texts:
            chunk_text = " ".join(current_texts).strip()
            chunks.append(
                TranscriptChunk(
                    chunk_id=f"chk_{uuid.uuid4().hex[:10]}",
                    chunk_index=chunk_idx,
                    start_time=round(chunk_start, 2),
                    end_time=round(last_seg_end, 2),
                    text=chunk_text,
                    topic_hint=self._detect_topic_hint(chunk_text),
                    preceding_context=self._get_last_sentences(prev_chunk_text, 2),
                    word_count=len(chunk_text.split()),
                )
            )

        return chunks


# Backward-compatible wrapper service class for Phase 1 references
class YouTubeService:
    """Convenience facade maintaining compatibility with Phase 1 caller endpoints."""

    extract_video_id = YouTubeURLParser.extract_video_id
    extract_playlist_id = YouTubeURLParser.extract_playlist_id
    is_valid_youtube_url = YouTubeURLParser.is_valid_youtube_url
    fetch_video_metadata = YouTubeMetadataFetcher.fetch_video_metadata
