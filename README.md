# Lectura AI 🎓

**Turn YouTube lectures into organised study notes.**

Lectura AI is a learning platform that helps students make better use of educational YouTube videos. You can add a single video or an entire playlist and generate study notes, revision summaries, flashcards, and quizzes from the content.

The idea behind the project is simple: instead of watching hours of lectures and making notes manually, students can get organised study material in one place. It also includes a fact-checking step to review AI-generated notes, a chatbot to ask questions about lectures, and progress tracking to help students revise more effectively.

## Features

- **YouTube Integration:** Add individual videos or complete playlists.
- **Study Notes:** Generate detailed notes, short revision notes, and last-minute summaries.
- **Fact Verification:** Check generated content for possible errors and unsupported information.
- **Flashcards & Quizzes:** Practise concepts through flashcards and interactive MCQs.
- **Lecture Chat:** Ask questions about video content and get answers with timestamps.
- **Progress Tracking:** Keep track of quiz scores, learning progress, and study activity.

## Tech Stack

**Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, Redis, Celery

**AI & Processing:** LangGraph, LangChain, OpenAI API, YouTube Transcript API

**Frontend:** React, TypeScript, Vite, Tailwind CSS, Zustand

**Other Tools:** Docker, Alembic, Recharts, Mermaid.js

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- OpenAI API key

### Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/Lectura-AI.git
cd Lectura-AI
```

Set up the environment files:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Add your API keys and database configuration to the environment files.

### Run with Docker

```bash
docker-compose up --build
```

Once running, access:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```text
Lectura-AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── services/
│   │   └── workflows/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── store/
│   └── package.json
├── docs/
├── docker-compose.yml
└── README.md
```

## License

MIT License
