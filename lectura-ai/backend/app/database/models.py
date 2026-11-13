import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database.connection import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"


class NoteType(str, PyEnum):
    COMPREHENSIVE = "comprehensive"
    REVISION = "revision"
    LAST_MINUTE = "last_minute"


class JobStatus(str, PyEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("LearningProgress", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    channel_name = Column(String(255), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    is_playlist = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="courses")
    playlists = relationship("Playlist", back_populates="course", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="course", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="course", cascade="all, delete-orphan")
    progress_records = relationship("LearningProgress", back_populates="course", cascade="all, delete-orphan")


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    youtube_playlist_id = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    channel_title = Column(String(255), nullable=True)
    video_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="playlists")
    videos = relationship("Video", back_populates="playlist")


class Video(Base):
    __tablename__ = "videos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    playlist_id = Column(String(36), ForeignKey("playlists.id", ondelete="SET NULL"), nullable=True, index=True)
    youtube_video_id = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    duration_seconds = Column(Integer, default=0, nullable=False)
    thumbnail_url = Column(String(1000), nullable=True)
    channel_name = Column(String(255), nullable=True)
    sequence_order = Column(Integer, default=1, nullable=False)
    processing_status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="videos")
    playlist = relationship("Playlist", back_populates="videos")
    transcript = relationship("Transcript", uselist=False, back_populates="video", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="video", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="video", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="video", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="video", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="video", cascade="all, delete-orphan")
    progress_records = relationship("LearningProgress", back_populates="video", cascade="all, delete-orphan")


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), unique=True, nullable=False)
    language = Column(String(20), default="en", nullable=False)
    is_generated = Column(Boolean, default=False, nullable=False)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    video = relationship("Video", back_populates="transcript")
    chunks = relationship("TranscriptChunk", back_populates="transcript", cascade="all, delete-orphan")


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transcript_id = Column(String(36), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    transcript = relationship("Transcript", back_populates="chunks")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    video = relationship("Video", back_populates="topics")


class Note(Base):
    __tablename__ = "notes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    note_type = Column(Enum(NoteType), default=NoteType.COMPREHENSIVE, nullable=False)
    title = Column(String(500), nullable=False)
    markdown_content = Column(Text, nullable=False)
    outline = Column(JSON, nullable=True)  # JSON array of hierarchical topics
    key_takeaways = Column(JSON, nullable=True)  # List of bullet summaries
    citations = Column(JSON, nullable=True)  # Timestamp references
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="notes")
    video = relationship("Video", back_populates="notes")
    verification_reports = relationship("VerificationReport", back_populates="note", cascade="all, delete-orphan")


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    workflow_name = Column(String(100), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    current_node = Column(String(100), nullable=True)
    progress_percentage = Column(Integer, default=0, nullable=False)
    logs = Column(JSON, default=list, nullable=False)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    video = relationship("Video", back_populates="agent_runs")


class VerificationReport(Base):
    __tablename__ = "verification_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    note_id = Column(String(36), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    rigor_score = Column(Float, default=1.0, nullable=False)  # 0.0 to 1.0
    is_verified = Column(Boolean, default=True, nullable=False)
    claims_verified_count = Column(Integer, default=0, nullable=False)
    discrepancies_found = Column(JSON, default=list, nullable=False)
    feedback_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    note = relationship("Note", back_populates="verification_reports")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    topic = Column(String(255), nullable=True)
    difficulty = Column(Integer, default=1, nullable=False)  # 1 easy, 2 medium, 3 hard
    ease_factor = Column(Float, default=2.5, nullable=False)  # SM-2 algorithm ease
    interval_days = Column(Integer, default=1, nullable=False)
    repetitions = Column(Integer, default=0, nullable=False)
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    next_review = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="flashcards")
    video = relationship("Video", back_populates="flashcards")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="quizzes")
    video = relationship("Video", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # Array of option strings
    correct_option_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    timestamp_reference = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score_percentage = Column(Float, nullable=False)
    user_answers = Column(JSON, nullable=False)  # Mapping question_id -> chosen index
    completed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("User", back_populates="quiz_attempts")


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String(36), ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    last_position_seconds = Column(Integer, default=0, nullable=False)
    notes_reviewed = Column(Boolean, default=False, nullable=False)
    quiz_completed = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="progress_records")
    course = relationship("Course", back_populates="progress_records")
    video = relationship("Video", back_populates="progress_records")
