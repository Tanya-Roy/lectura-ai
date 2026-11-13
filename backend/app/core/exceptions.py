from typing import Any, Dict, Optional


class LecturaBaseException(Exception):
    """Base exception class for all Lectura AI domain exceptions."""

    def __init__(
        self,
        message: str = "An internal error occurred in Lectura AI",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class VideoProcessingError(LecturaBaseException):
    """Raised when processing a video or playlist fails during ingestion or synthesis."""

    def __init__(self, message: str = "Video processing failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=422, details=details)


class TranscriptNotAvailableError(LecturaBaseException):
    """Raised when subtitles or transcripts are not available for a video."""

    def __init__(
        self,
        message: str = "Transcript not available for this video or disabled by owner",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=404, details=details)


class NotFoundError(LecturaBaseException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=404, details=details)


class UnauthorizedError(LecturaBaseException):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Could not validate credentials", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=401, details=details)


class ForbiddenError(LecturaBaseException):
    """Raised when user does not have permission for the resource."""

    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=403, details=details)


class WorkflowExecutionError(LecturaBaseException):
    """Raised when LangGraph agent workflow fails during step execution."""

    def __init__(self, message: str = "Workflow execution failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=500, details=details)
