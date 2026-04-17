import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.repositories.analytics_repo import AnalyticsRepository
from app.models.core import Repository,Vulnerability
from app.utils.pdf_generator import generate_soc2_audit_report

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

    # Fetch metrics concurrently or sequentially
    summary_stats = await repo.get_summary_stats()
    severity_distribution = await repo.get_severity_distribution()
    status_distribution = await repo.get_status_distribution()
    top_vulnerable_files = await repo.get_top_vulnerable_files()
    vulnerabilities_by_repo = await repo.get_vulnerabilities_by_repo()

    return {
        "summary": summary_stats,
        "severity_distribution": severity_distribution,
        "status_distribution": status_distribution,
        "top_vulnerable_files": top_vulnerable_files,
        "vulnerabilities_by_repo": vulnerabilities_by_repo
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

@router.get("/report/soc2/pdf")
async def download_soc2_pdf(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user) # Ensure only authorized users can download!
):
    """
    Generates and returns a PDF file containing the SOC2 audit log.
    """
    # 1. Verify Repo exists
    repo = await db.get(Repository, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    analytics_repo = AnalyticsRepository(db)
    
    # 2. Fetch Vulnerability Data
    vulnerabilities = await analytics_repo.get_vulnerability_data(repository_id)

    # 3. Generate PDF
    pdf_buffer = generate_soc2_audit_report(
        repo_name=repo.full_name,
        vulnerabilities=vulnerabilities,
        start_date="2026-01-01", #TODO:  You can pass these dynamically via query params later
        end_date=datetime.utcnow().strftime('%Y-%m-%d')
    )

    # 4. Stream the file directly to the user's browser
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=SOC2_Audit_{repo.name}.pdf"
        }
    )
