# Lectura AI - System Architecture 📐

## Overview
Lectura AI is a high-assurance, multi-agent AI system designed to convert educational YouTube videos and playlists into rigorous university-grade study materials.

```mermaid
flowchart TD
    User["Student / Scholar"] -->|Pastes YouTube URL| Frontend["React + TypeScript UI"]
    Frontend -->|POST /api/videos/process| Gateway["FastAPI REST API"]
    
    subgraph MultiAgentPipeline["LangGraph Multi-Agent Pipeline"]
        Ingest["Ingestion Agent\n(Transcript & Metadata)"] --> Segmentation["Segmentation Agent\n(Semantic Topics)"]
        Segmentation --> Synthesizer["Synthesis Agent\n(3-Tiered Academic Notes)"]
        Synthesizer --> Verifier["Verification Agent\n(Formula & Claim Audit)"]
        Verifier --> ActiveRecall["Active Recall Agent\n(Flashcards & Quizzes)"]
        ActiveRecall --> Persist["Persistence & Event Bus"]
    end

    Gateway --> Ingest
    Persist --> DB[(PostgreSQL 16)]
    Persist --> Cache[(Redis 7)]
    Frontend -->|Polls /api/jobs/{id}| Gateway
```

---

## Backend Component Topology

### 1. Ingestion Engine (`app/services/youtube_service.py`)
- **Video ID & Playlist Extraction**: Validates URLs against regex patterns for standard watch URLs, short URLs (`youtu.be`), playlist URLs, and embed URLs.
- **Transcript Acquisition**: Fetches manual subtitles or auto-generated transcripts with fallback language cascading using `youtube-transcript-api`.
- **Semantic Windowing**: Aggregates timestamp segments into ~2-minute semantic chunks.

### 2. Multi-Agent Orchestration (`app/workflows/`)
Built with **LangGraph**:
- `ingest_video`: Extracts metadata via oEmbed and fetches transcript chunks.
- `extract_structure`: Segments transcripts into hierarchical lecture topics.
- `generate_notes`: Synthesizes 3 distinct note representations:
  - **Comprehensive Master Notes**: Deep academic explanations with LaTeX equations and citations.
  - **Revision Summary**: High-yield cheat sheets and comparison tables.
  - **Last-Minute Flash Notes**: 5-minute pre-exam memory anchors.
- `verify_notes`: Fact-checking agent auditing mathematical formulas and scoring academic rigor (0.0 - 1.0).
- `generate_active_recall`: Constructs SM-2 spaced repetition flashcards and multiple-choice quizzes with timestamp citations.

### 3. Data Tier (`app/database/`)
- **Async Engine**: SQLAlchemy 2.0 with `asyncpg` connection pooling.
- **Schema Migrations**: Managed via Alembic (`001_initial_schema.py`).
- **Relational Entities**:
  - `User`, `Course`, `Playlist`, `Video`
  - `Transcript`, `TranscriptChunk`, `Topic`
  - `Note`, `AgentRun`, `VerificationReport`
  - `Flashcard`, `Quiz`, `QuizQuestion`, `QuizAttempt`, `LearningProgress`

---

## Frontend Architecture

- **SPA Routing**: React Router v6 with `AppLayout` and dedicated workspaces.
- **State Layer**: Zustand for application-level state (active course, active video, background job status) + TanStack Query for cache invalidation.
- **Component Primitives**: Radix UI primitives wrapped in accessible Tailwind styles (`@/components/ui`).
- **Mathematical Typography**: KaTeX & Rehype-KaTeX rendering LaTeX syntax inline (`$..$`) and display mode (`$$..$$`).
- **Observability**: Real-time polling via `useJobPolling` reflecting LangGraph node transitions and log streams.
