# Lectura AI 🎓

> **Transform YouTube Content into Verified, Structured University-Grade Study Notes**

Lectura AI is a production-grade, AI-powered learning platform that converts single YouTube videos and entire course playlists into comprehensive, verified study materials. Built with an agentic multi-stage pipeline, it extracts transcripts, synthesizes hierarchical academic notes, generates flashcards, interactive quizzes, and allows you to chat with your video content.

---

## 🌟 Key Features

- 📹 **YouTube Video & Playlist Ingestion**: Ingest single videos or multi-video lecture series automatically with metadata and transcript extraction.
- 📝 **Multi-Tiered Academic Notes**:
  - **Comprehensive Master Notes**: Deep academic breakdowns with LaTeX equations, diagrams, and timestamped citations.
  - **Executive Revision Notes**: High-yield summaries with cheat sheets and formula tables.
  - **Last-Minute Flash Notes**: 5-minute pre-exam memory anchors and core definitions.
- 🔍 **Fact-Checking & Verification Agent**: Detects hallucinations, verifies mathematical formulas, cross-checks claims, and scores academic rigor.
- 🧠 **Active Recall Suite**: Automatic spaced-repetition flashcard generation and adaptive multiple-choice quizzes.
- 💬 **Interactive Lecture Chatbot**: Ask questions directly to the video context with pinpoint timestamp citations.
- 📊 **Mastery Analytics**: Track progress, quiz scores, and study streak over time.

---

## 🏗️ Architecture & Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16 with async SQLAlchemy 2.0 & asyncpg
- **Migrations**: Alembic
- **Caching & Queues**: Redis 7 & Celery
- **Agent Orchestration**: LangGraph & LangChain (OpenAI GPT-4o / GPT-4o-mini)
- **Transcription**: `youtube-transcript-api` with fallback mechanisms
- **Security**: JWT Authentication (python-jose), bcrypt password hashing

### Frontend
- **Framework**: React 18 with TypeScript & Vite
- **Styling**: Tailwind CSS & Lucide Icons
- **State Management**: Zustand & TanStack Query (React Query)
- **UI System**: Radix UI primitives with custom accessible Tailwind styling
- **Rich Content**: React Markdown, Rehype-KaTeX (LaTeX rendering), Mermaid.js diagrams, Recharts analytics

---

## 🚀 Quick Start Guide

### Prerequisites
- Docker & Docker Compose installed
- Python 3.11+ & Node.js 18+ (for local bare-metal development)
- OpenAI API Key (or compatible LLM provider)

### 1. Clone & Configure Environment

```bash
git clone https://github.com/your-org/lectura-ai.git
cd lectura-ai

# Copy environment variables
cp .env.example .env
cp backend/.env.example backend/.env
```

Edit `.env` and `backend/.env` with your API keys (e.g., `OPENAI_API_KEY`).

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`

---

## 💻 Local Development Setup

### Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure

```
lectura-ai/
├── docker-compose.yml          # Container orchestration
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
├── docs/                       # Architecture & API specifications
│   ├── architecture.md
│   ├── api.md
│   ├── decisions.md
│   └── development_log.md
├── backend/
│   ├── alembic/                # Database migrations
│   ├── app/
│   │   ├── api/                # FastAPI endpoint routers
│   │   ├── core/               # Logging, security, exceptions
│   │   ├── database/           # SQLAlchemy models, schemas, connection
│   │   ├── services/           # YouTube and external services
│   │   ├── workflows/          # LangGraph agent workflows
│   │   ├── config.py           # Pydantic environment settings
│   │   ├── dependencies.py     # FastAPI dependencies (auth, db)
│   │   └── main.py             # App initialization and middleware
│   ├── tests/                  # Pytest test suite
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/         # UI primitives & layouts
    │   ├── hooks/              # Custom hooks (polling, queries)
    │   ├── pages/              # Real application views
    │   ├── services/           # Axios API client
    │   ├── store/              # Zustand global state
    │   ├── types/              # TypeScript schema interfaces
    │   ├── App.tsx             # Route definitions
    │   └── main.tsx
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.ts
```

---

## 📄 License

MIT License. Built for education and lifelong learning.
