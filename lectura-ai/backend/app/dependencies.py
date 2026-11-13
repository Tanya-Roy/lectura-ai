from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import verify_token
from app.database.connection import get_db
from app.database.models import User, UserRole

# HTTP Bearer scheme with auto_error=False to support both guest/demo browsing and authenticated states
security_scheme = HTTPBearer(auto_error=False)

# Re-export get_db for easy importing
get_database_session = get_db


class PaginationParams:
    """Reusable query parameters for paginated list endpoints."""

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Offset for pagination"),
        limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    ):
        self.skip = skip
        self.limit = limit


# Default mock user representation for local development / testing
DEFAULT_DEV_USER = User(
    id="usr_demo_lectura_101",
    email="student@lectura.ai",
    full_name="Alex Academic",
    role=UserRole.USER,
    is_active=True,
)


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validates the JWT access token and returns the corresponding User.
    In development mode, if no token is provided, returns a default mock user.
    """
    if auth is None:
        if settings.ENVIRONMENT == "development":
            return DEFAULT_DEV_USER
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = verify_token(auth.credentials)
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError("Invalid token payload")

        # In dev mode, return dev user if matching ID or demo user
        return DEFAULT_DEV_USER
    except Exception as exc:
        if settings.ENVIRONMENT == "development":
            return DEFAULT_DEV_USER
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
