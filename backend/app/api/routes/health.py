from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/health", status_code=200)
async def health_check():
    """
    Simple health check endpoint to verify the API is running.
    Perfect for CI/CD pipelines or deployment platforms like Render to check uptime.
    """
    return {
        "status": "Healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
