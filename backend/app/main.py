from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import chat, courses, health, jobs, notes, playlists, progress, quizzes, videos
from app.config import settings
from app.core.exceptions import LecturaBaseException
from app.core.logging import logger
from app.database.connection import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in [{settings.ENVIRONMENT}] mode")

    # In development mode, automatically create tables if not existing
    if settings.ENVIRONMENT == "development":
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema initialized successfully.")
        except Exception as exc:
            logger.warning(f"Could not connect to database on startup (running in mock mode): {exc}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}...")
    await engine.dispose()
    logger.info("Database engine connections closed.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Lectura AI is a high-performance, agentic learning platform that transforms YouTube videos "
        "and playlists into verified, multi-tiered university study notes, interactive quizzes, "
        "and spaced-repetition flashcards."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler for custom domain exceptions
@app.exception_handler(LecturaBaseException)
async def lectura_exception_handler(request: Request, exc: LecturaBaseException):
    logger.warning(f"Domain exception on {request.url.path}: {exc.message} (status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


# General fallback exception handler
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again or contact support.",
        },
    )


# Include all API Routers
app.include_router(health.router, prefix="/api")
app.include_router(videos.router, prefix="/api")
app.include_router(playlists.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(notes.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(quizzes.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")


@app.get("/", tags=["Root"])
async def root():
    """Root redirect / landing check."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health",
    }
