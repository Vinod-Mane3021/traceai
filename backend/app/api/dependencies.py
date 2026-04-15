from typing import AsyncGenerator
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/github/callback")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts the JWT token from the request header, decodes it, 
    and validates the user's session.
    """
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
        
        # For now, simply returning the parsed username is enough.
        # TODO: If you add a User table to your DB later, you can use the DB session 
        # here to fetch the full user record.
        return {"username": username}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    
    except jwt.InvalidTokenError:
        raise credentials_exception