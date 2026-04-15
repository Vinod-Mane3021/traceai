from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.repositories.analytics_repo import AnalyticsRepository

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
async def get_analytics_overview(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Aggregates all core metrics into a single payload for the React dashboard landing page.
    """

    repo = AnalyticsRepository(db)

    # Run queries concurrently if needed, or await them sequentially
    severity_distribution = await repo.get_severity_distribution()
    top_vulnerable_files = await repo.get_top_vulnerable_files()

    return {
        "severity_distribution": severity_distribution,
        "top_vulnerable_files": top_vulnerable_files,
        # You can easily expand this to include total PRs scanned, etc.
    }

@router.get("/feed")
async def get_vulnerability_feed(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Returns the most recent security events."""
    repo = AnalyticsRepository(db)
    recent_vulnerabilities = await repo.get_recent_vulnerabilities(limit)
    return {"recent_vulnerabilities": recent_vulnerabilities}