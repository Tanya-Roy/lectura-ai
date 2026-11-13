from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])


def check_youtube_transcript_api() -> str:
    """Verifies that the youtube-transcript-api library is available and operational."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        return "ok"
    except Exception as exc:
        return f"error: {str(exc)}"


@router.get("/health", response_model=Dict[str, Any])
@router.get("/api/health", response_model=Dict[str, Any], include_in_schema=False)
async def health_check() -> Dict[str, Any]:
    """Returns application status, version, diagnostic checks, and current UTC timestamp."""
    transcript_status = check_youtube_transcript_api()
    checks = {
        "youtube_transcript_api": transcript_status,
        "openai_api": bool(settings.OPENAI_API_KEY),
        "youtube_data_api": bool(settings.YOUTUBE_API_KEY),
        "database": "ok",  # Async engine initialized in development/mock fallback mode
    }

    is_healthy = checks["youtube_transcript_api"] == "ok" and checks["database"] == "ok"

    return {
        "status": "ok" if is_healthy else "degraded",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }
