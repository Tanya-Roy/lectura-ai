# Lectura AI - REST API Reference 📑

Base URL: `http://localhost:8000/api`  
Interactive Swagger Docs: `http://localhost:8000/docs`

---

## 1. Health & Status

### `GET /health`
Returns system health, version, and current UTC timestamp.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2026-11-02T10:30:00Z",
  "environment": "development"
}
```

---

## 2. Videos & Ingestion

### `POST /videos/process`
Submits a YouTube video or playlist URL for background agent processing.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "course_id": "optional_course_id",
  "generate_flashcards": true,
  "generate_quizzes": true,
  "detailed_transcription": true
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "job_a1b2c3d4e5f6",
  "video_id": "dQw4w9WgXcQ",
  "course_id": "crs_ml_101",
  "status": "in_progress",
  "workflow_name": "youtube_synthesis_pipeline",
  "current_node": "ingest_video",
  "progress_percentage": 25,
  "logs": [],
  "started_at": "2026-11-02T10:30:00Z"
}
```

### `GET /videos/{video_id}`
Retrieves video metadata, processing status, and topic hierarchy.

### `GET /videos/{video_id}/transcript`
Retrieves raw transcript and timestamped chunk sequences.

---

## 3. Courses & Playlists

### `GET /courses`
Lists enrolled courses for the authenticated user.

### `POST /courses`
Creates a new course container.

### `GET /courses/{course_id}`
Returns course metadata with all enrolled lecture videos.

### `GET /playlists/{playlist_id}`
Fetches YouTube playlist details and all indexed videos.

---

## 4. Study Notes & Verification

### `GET /notes`
Filters study notes by `course_id`, `video_id`, or `note_type` (`comprehensive`, `revision`, `last_minute`).

### `GET /notes/{note_id}`
Returns full Markdown note body with outline, key takeaways, citations, and verification report.

### `GET /notes/{note_id}/export/{format}`
Exports note content as `markdown`, `pdf`, or `docx`.

---

## 5. Quizzes & Active Recall

### `GET /quizzes`
Retrieves diagnostic multiple-choice quizzes.

### `POST /quizzes/{quiz_id}/submit`
Submits user answers, calculates score percentage, and returns question explanations with timestamp citations.

### `GET /flashcards`
Retrieves spaced-repetition flashcards.

### `POST /flashcards/{flashcard_id}/review`
Submits SM-2 memory recall rating (1-5) and updates next review date.

---

## 6. AI Lecture Chat

### `POST /chat`
Interactive Q&A grounded in transcript and lecture notes.

**Request Body:**
```json
{
  "message": "Why is L2 regularization necessary in this formulation?",
  "video_id": "vid_ml_01",
  "history": []
}
```

**Response:**
```json
{
  "message": "In this lecture, L2 regularization is added to enforce strict convexity...",
  "citations": [
    {
      "timestamp_seconds": 245.0,
      "label": "04:05 - Regularization Definition",
      "snippet": "Notice that minimizing unconstrained training loss leads to acute overfitting..."
    }
  ],
  "suggested_followups": [
    "What is the difference between L1 and L2 regularization here?",
    "Show me a flashcard on this concept."
  ]
}
```

---

## 7. Job Polling & Observability

### `GET /jobs/{job_id}`
Polls real-time state, logs, current node, and progress percentage.

### `GET /progress/summary`
Returns aggregated analytics (study minutes, streak, quiz accuracy).
