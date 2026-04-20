import structlog
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.services.analytics_service import AnalyticsService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
async def get_analytics_overview(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Aggregates all core metrics into a single payload for the React dashboard landing page.
    """
    log = logger.bind(user_id=current_user.get("id"), endpoint="get_analytics_overview")
    log.info("request_received")
    
    service = AnalyticsService(db)
    stats = await service.get_overview_stats()
    
    log.info("request_completed")
    return stats

@router.get("/feed")
async def get_vulnerability_feed(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Returns the most recent security events."""
    log = logger.bind(user_id=current_user.get("id"), limit=limit, endpoint="get_vulnerability_feed")
    log.info("request_received")
    
    service = AnalyticsService(db)
    feed = await service.get_vulnerability_feed(limit)
    
    log.info("request_completed")
    return feed

@router.get("/report/soc2/pdf")
async def download_soc2_pdf(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generates and returns a PDF file containing the SOC2 audit log.
    """
    log = logger.bind(user_id=current_user.get("id"), repository_id=repository_id, endpoint="download_soc2_pdf")
    log.info("request_received")
    
    service = AnalyticsService(db)
    pdf_buffer, repo_name = await service.generate_soc2_report(repository_id)
    
    if not pdf_buffer:
        log.warning("report_generation_failed", reason="repository_not_found")
        raise HTTPException(status_code=404, detail="Repository not found")

    log.info("request_completed")
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=SOC2_Audit_{repo_name}.pdf"
        }
    )
