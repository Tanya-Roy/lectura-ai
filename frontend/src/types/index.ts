export type UserRole = "user" | "admin";
export type NoteType = "comprehensive" | "revision" | "last_minute";
export type JobStatus = "pending" | "in_progress" | "completed" | "failed";

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Video {
  id: string;
  course_id: string;
  playlist_id?: string;
  youtube_video_id: string;
  title: string;
  description?: string;
  duration_seconds: number;
  thumbnail_url?: string;
  channel_name?: string;
  sequence_order: number;
  processing_status: JobStatus;
  created_at: string;
  transcript?: Transcript;
  topics?: Topic[];
}

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
}

export interface TranscriptChunk {
  id?: string;
  chunk_id?: string;
  chunk_index: number;
  start_time: number;
  end_time: number;
  text: string;
  topic_hint?: string;
  preceding_context?: string;
  word_count?: number;
}

export interface Transcript {
  id: string;
  video_id: string;
  language: string;
  is_generated: boolean;
  raw_text: string;
  cleaned_text?: string;
  chunks: TranscriptChunk[];
}

export interface Topic {
  id: string;
  title: string;
  summary?: string;
  start_time: number;
  end_time: number;
  order_index: number;
}

export interface Course {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  channel_name?: string;
  thumbnail_url?: string;
  is_playlist: boolean;
  created_at: string;
  updated_at: string;
  video_count?: number;
  videos?: Video[];
}

export interface VerificationReport {
  id: string;
  note_id: string;
  rigor_score: number;
  is_verified: boolean;
  claims_verified_count: number;
  discrepancies_found: any[];
  feedback_notes?: string;
  created_at: string;
}

export interface Note {
  id: string;
  course_id: string;
  video_id?: string;
  note_type: NoteType;
  title: string;
  markdown_content?: string;
  outline?: { title: string; timestamp?: number }[];
  key_takeaways?: string[];
  citations?: { timestamp_seconds: number; label: string; snippet: string }[];
  version: number;
  created_at: string;
  updated_at: string;
  verification_reports?: VerificationReport[];
}

export interface Flashcard {
  id: string;
  course_id: string;
  video_id?: string;
  front: string;
  back: string;
  topic?: string;
  difficulty: number;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  last_reviewed?: string;
  next_review: string;
  created_at: string;
}

export interface QuizQuestion {
  id: string;
  quiz_id: string;
  question_text: string;
  options: string[];
  correct_option_index?: number;
  explanation?: string;
  timestamp_reference?: number;
}

export interface Quiz {
  id: string;
  course_id: string;
  video_id?: string;
  title: string;
  description?: string;
  created_at: string;
  questions: QuizQuestion[];
}

export interface QuizAttempt {
  id: string;
  quiz_id: string;
  user_id: string;
  score_percentage: number;
  user_answers: Record<string, number>;
  completed_at: string;
}

export interface LearningProgress {
  id: string;
  user_id: string;
  course_id: string;
  video_id?: string;
  is_completed: boolean;
  last_position_seconds: number;
  notes_reviewed: boolean;
  quiz_completed: boolean;
  updated_at: string;
}

export interface JobLog {
  timestamp: string;
  node: string;
  message: string;
  level?: "info" | "warning" | "error";
}

export interface JobResponse {
  job_id: string;
  video_id?: string;
  course_id?: string;
  playlist_id?: string;
  status: JobStatus;
  workflow_name: string;
  current_node?: string;
  progress_percentage: number;
  logs: JobLog[];
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface Citation {
  timestamp_seconds: number;
  label: string;
  snippet: string;
}

export interface ChatMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  timestamp?: string;
}

export interface ChatResponse {
  message: string;
  citations: Citation[];
  suggested_followups: string[];
}

// ==========================================
// Phase 2 Metadata & Preview Types
// ==========================================

export interface VideoMetadata {
  video_id: string;
  title: string;
  channel_name: string;
  channel_url: string;
  thumbnail_url: string;
  duration_seconds: number;
  description: string;
}

export interface PlaylistVideoItem {
  video_id: string;
  title: string;
  thumbnail_url: string;
  position: number;
  channel_name: string;
}

export interface PlaylistMetadata {
  playlist_id: string;
  title: string;
  channel_name: string;
  description: string;
  video_count: number;
  thumbnail_url: string;
  videos: PlaylistVideoItem[];
}

export interface URLPreviewResponse {
  valid: boolean;
  url_type: "video" | "playlist" | "video_in_playlist" | "invalid";
  video_id?: string;
  playlist_id?: string;
  metadata?: VideoMetadata | PlaylistMetadata | any;
  error?: string;
}

export interface TranscriptUploadResponse {
  video_id: string;
  parse_format: string;
  segment_count: number;
  chunk_count: number;
  duration_seconds: number;
  warnings: string[];
  chunks: TranscriptChunk[];
}
