import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.analytics_repo import AnalyticsRepository
from app.models.core import Repository
from app.utils.pdf_generator_html_to_pdf import generate_soc2_audit_report
from datetime import datetime, timezone

logger = structlog.get_logger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AnalyticsRepository(db)

    async def get_overview_stats(self):
        log = logger.bind(method="get_overview_stats")
        log.info("starting_analytics_overview_aggregation", message="Aggregating all core metrics for the dashboard overview")
        
        summary_stats = await self.repo.get_summary_stats()
        severity_distribution = await self.repo.get_severity_distribution()
        status_distribution = await self.repo.get_status_distribution()
        top_vulnerable_files = await self.repo.get_top_vulnerable_files()
        vulnerabilities_by_repo = await self.repo.get_vulnerabilities_by_repo()

        log.info("analytics_overview_aggregation_completed", 
                 message="Successfully aggregated analytics overview stats",
                 total_vulns=summary_stats.get("total_vulnerabilities"),
                 open_vulns=summary_stats.get("open_vulnerabilities"))

        return {
            "summary": summary_stats,
            "severity_distribution": severity_distribution,
            "status_distribution": status_distribution,
            "top_vulnerable_files": top_vulnerable_files,
            "vulnerabilities_by_repo": vulnerabilities_by_repo
        }

    async def get_vulnerability_feed(self, limit: int = 10):
        log = logger.bind(method="get_vulnerability_feed", limit=limit)
        log.info("fetching_recent_vulnerabilities_feed", message=f"Retrieving the {limit} most recent security events")
        
        recent_vulnerabilities = await self.repo.get_recent_vulnerabilities(limit)
        
        log.info("recent_vulnerabilities_feed_retrieved", message="Successfully fetched vulnerability feed", count=len(recent_vulnerabilities))
        return {"recent_vulnerabilities": recent_vulnerabilities}

    async def generate_soc2_report(self, repository_id: int | None = None, github_id: int | None = None):
        log = logger.bind(method="generate_soc2_report", repository_id=repository_id, github_id=github_id)
        
        # 1. Verify Repo exists
        if repository_id:
            repo = await self.db.get(Repository, repository_id)
        elif github_id:
            stmt = select(Repository).where(Repository.github_id == github_id)
            result = await self.db.execute(stmt)
            repo = result.scalar_one_or_none()
        else:
            log.warning("missing_repository_identifier", message="Failed to generate SOC2 report: Neither repository_id nor github_id provided")
            return None, None

        if not repo:
            log.warning("repo_not_found_for_report_generation", message="Failed to generate SOC2 report: Repository not found")
            return None, None
        
        log.info("starting_soc2_pdf_generation", message=f"Starting SOC2 PDF generation for {repo.full_name}")
        
        # 2. Fetch Vulnerability Data
        vulnerabilities = await self.repo.get_vulnerability_data(repo.id)

        # 3. Generate PDF
        pdf_buffer = generate_soc2_audit_report(
            repo_name=repo.full_name,
            vulnerabilities=vulnerabilities,
            start_date="2026-01-01", 
            end_date=datetime.now(timezone.utc).strftime('%Y-%m-%d')
        )
        
        log.info("soc2_pdf_generation_completed", message="Successfully generated SOC2 PDF report", repo_name=repo.full_name, vuln_count=len(vulnerabilities))
        return pdf_buffer, repo.name
