from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.database.models import JobStatus, NoteType, UserRole


# Base schema configuration
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Authentication & Users ---
class UserBase(BaseSchema):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserResponse(UserBase):
    id: str
    role: UserRole
    is_active: bool
    created_at: datetime


class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseSchema):
    sub: str
    exp: Optional[int] = None


# --- Video & Ingestion ---
class VideoProcessRequest(BaseModel):
    url: str = Field(description="YouTube video or playlist URL")
    course_id: Optional[str] = Field(default=None, description="Optional existing course to associate with")
    generate_flashcards: bool = True
    generate_quizzes: bool = True
    detailed_transcription: bool = True


class TranscriptChunkResponse(BaseSchema):
    id: str
    chunk_index: int
    start_time: float
    end_time: float
    text: str


class TranscriptResponse(BaseSchema):
    id: str
    video_id: str
    language: str
    is_generated: bool
    raw_text: str
    cleaned_text: Optional[str] = None
    chunks: List[TranscriptChunkResponse] = []


class TopicResponse(BaseSchema):
    id: str
    title: str
    summary: Optional[str] = None
    start_time: float
    end_time: float
    order_index: int


class VideoResponse(BaseSchema):
    id: str
    course_id: str
    playlist_id: Optional[str] = None
    youtube_video_id: str
    title: str
    description: Optional[str] = None
    duration_seconds: int
    thumbnail_url: Optional[str] = None
    channel_name: Optional[str] = None
    sequence_order: int
    processing_status: JobStatus
    created_at: datetime


class VideoDetailResponse(VideoResponse):
    transcript: Optional[TranscriptResponse] = None
    topics: List[TopicResponse] = []


# --- Playlists ---
class PlaylistResponse(BaseSchema):
    id: str
    course_id: str
    youtube_playlist_id: str
    title: str
    description: Optional[str] = None
    channel_title: Optional[str] = None
    video_count: int
    created_at: datetime
    videos: List[VideoResponse] = []


# --- Courses ---
class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None
    channel_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_playlist: bool = False


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class CourseResponse(BaseSchema):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    channel_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_playlist: bool
    created_at: datetime
    updated_at: datetime
    video_count: Optional[int] = 0


class CourseDetailResponse(CourseResponse):
    videos: List[VideoResponse] = []
    playlists: List[PlaylistResponse] = []


# --- Notes & Verification ---
class VerificationReportResponse(BaseSchema):
    id: str
    note_id: str
    rigor_score: float
    is_verified: bool
    claims_verified_count: int
    discrepancies_found: List[Dict[str, Any]] = []
    feedback_notes: Optional[str] = None
    created_at: datetime


class NoteCreate(BaseModel):
    course_id: str
    video_id: Optional[str] = None
    note_type: NoteType = NoteType.COMPREHENSIVE
    title: str
    markdown_content: str
    outline: Optional[List[Dict[str, Any]]] = None
    key_takeaways: Optional[List[str]] = None
    citations: Optional[List[Dict[str, Any]]] = None


class NoteResponse(BaseSchema):
    id: str
    course_id: str
    video_id: Optional[str] = None
    note_type: NoteType
    title: str
    outline: Optional[List[Dict[str, Any]]] = None
    key_takeaways: Optional[List[str]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    version: int
    created_at: datetime
    updated_at: datetime


class NoteDetailResponse(NoteResponse):
    markdown_content: str
    verification_reports: List[VerificationReportResponse] = []


# --- Flashcards ---
class FlashcardCreate(BaseModel):
    course_id: str
    video_id: Optional[str] = None
    front: str
    back: str
    topic: Optional[str] = None
    difficulty: int = 1


class FlashcardReviewRequest(BaseModel):
    rating: int = Field(ge=1, le=5, description="User memory recall rating 1-5")


class FlashcardResponse(BaseSchema):
    id: str
    course_id: str
    video_id: Optional[str] = None
    front: str
    back: str
    topic: Optional[str] = None
    difficulty: int
    ease_factor: float
    interval_days: int
    repetitions: int
    last_reviewed: Optional[datetime] = None
    next_review: datetime
    created_at: datetime


# --- Quizzes ---
class QuizQuestionResponse(BaseSchema):
    id: str
    quiz_id: str
    question_text: str
    options: List[str]
    correct_option_index: Optional[int] = None  # Hidden during active quiz unless submitted
    explanation: Optional[str] = None
    timestamp_reference: Optional[float] = None


class QuizResponse(BaseSchema):
    id: str
    course_id: str
    video_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    created_at: datetime
    questions: List[QuizQuestionResponse] = []


class QuizSubmitRequest(BaseModel):
    answers: Dict[str, int] = Field(description="Map of question_id to selected option index")


class QuizAttemptResponse(BaseSchema):
    id: str
    quiz_id: str
    user_id: str
    score_percentage: float
    user_answers: Dict[str, int]
    completed_at: datetime


# --- Learning Progress ---
class ProgressUpdate(BaseModel):
    last_position_seconds: Optional[int] = None
    is_completed: Optional[bool] = None
    notes_reviewed: Optional[bool] = None
    quiz_completed: Optional[bool] = None


class ProgressResponse(BaseSchema):
    id: str
    user_id: str
    course_id: str
    video_id: Optional[str] = None
    is_completed: bool
    last_position_seconds: int
    notes_reviewed: bool
    quiz_completed: bool
    updated_at: datetime


# --- Jobs & Processing ---
class JobResponse(BaseSchema):
    job_id: str
    video_id: Optional[str] = None
    course_id: Optional[str] = None
    playlist_id: Optional[str] = None
    status: JobStatus
    workflow_name: str
    current_node: Optional[str] = None
    progress_percentage: int
    logs: List[Dict[str, Any]] = []
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


# --- Chat & QA Assistant ---
class Citation(BaseModel):
    timestamp_seconds: float
    label: str
    snippet: str


class ChatMessage(BaseModel):
    role: str = Field(description="'user' or 'assistant'")
    content: str
    citations: Optional[List[Citation]] = None


class ChatRequest(BaseModel):
    video_id: Optional[str] = None
    course_id: Optional[str] = None
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    message: str
    citations: List[Citation] = []
    suggested_followups: List[str] = []


# ==========================================
# Phase 2 Schemas: Ingestion & Previews
# ==========================================


class URLPreviewRequest(BaseModel):
    url: str


class VideoPreviewResponse(BaseModel):
    valid: bool
    url_type: str  # "video" | "playlist" | "video_in_playlist" | "invalid"
    video_id: Optional[str] = None
    playlist_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TranscriptUploadResponse(BaseModel):
    video_id: str
    parse_format: str  # "srt" | "vtt" | "txt"
    segment_count: int
    chunk_count: int
    duration_seconds: float
    warnings: List[str]
    chunks: List[TranscriptChunkResponse]


class PlaylistProcessRequest(BaseModel):
    url: str
    max_videos: int = 50
    generate_flashcards: bool = True
    generate_quizzes: bool = True

