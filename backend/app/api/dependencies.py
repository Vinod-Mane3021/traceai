from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from app.core.database import async_session_maker
from app.core.config import settings

# ---------------------------------------------------------
# Database Dependency
# ---------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates and yields an asynchronous database session.
    Automatically closes the session when the request is finished.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

# ---------------------------------------------------------
# Authentication Dependency
# ---------------------------------------------------------

# This tells FastAPI to look for an "Authorization: Bearer <token>" header
# We set auto_error=False to handle the logic manually inside get_current_user,
# which allows it to be fully dynamic based on the settings.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/github/callback", 
    auto_error=False
)

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> dict:
    """
    Extracts the JWT token from the request header, decodes it, 
    and validates the user's session.
    
    If AUTH_MIDDLEWARE_ENABLED is False, authentication is skipped.
    """
    # Check boolean value (Pydantic handles string "False" to bool False conversion)
    if not settings.AUTH_MIDDLEWARE_ENABLED:
        # Return a dummy user for development/testing
        return {"username": "guest", "is_authenticated": False}

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the local JWT. 
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        return {"username": username, "is_authenticated": True}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    
    except jwt.InvalidTokenError:
        raise credentials_exception
