import structlog
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
        log.info("fetching_overview_stats")
        
        summary_stats = await self.repo.get_summary_stats()
        severity_distribution = await self.repo.get_severity_distribution()
        status_distribution = await self.repo.get_status_distribution()
        top_vulnerable_files = await self.repo.get_top_vulnerable_files()
        vulnerabilities_by_repo = await self.repo.get_vulnerabilities_by_repo()

        log.info("overview_stats_fetched", 
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
        log.info("fetching_vulnerability_feed")
        
        recent_vulnerabilities = await self.repo.get_recent_vulnerabilities(limit)
        
        log.info("vulnerability_feed_fetched", count=len(recent_vulnerabilities))
        return {"recent_vulnerabilities": recent_vulnerabilities}

    async def generate_soc2_report(self, repository_id: int):
        log = logger.bind(method="generate_soc2_report", repository_id=repository_id)
        
        # 1. Verify Repo exists
        repo = await self.db.get(Repository, repository_id)
        if not repo:
            log.warning("repo_not_found")
            return None, None
        
        log.info("generating_soc2_pdf", repo_name=repo.full_name)
        
        # 2. Fetch Vulnerability Data
        vulnerabilities = await self.repo.get_vulnerability_data(repository_id)

        # 3. Generate PDF
        pdf_buffer = generate_soc2_audit_report(
            repo_name=repo.full_name,
            vulnerabilities=vulnerabilities,
            start_date="2026-01-01", 
            end_date=datetime.now(timezone.utc).strftime('%Y-%m-%d')
        )
        
        log.info("soc2_pdf_generated", repo_name=repo.full_name, vuln_count=len(vulnerabilities))
        return pdf_buffer, repo.name
