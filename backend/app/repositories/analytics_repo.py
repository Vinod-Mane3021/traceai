import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.core import Repository, PullRequest, Vulnerability

logger = structlog.get_logger(__name__)

class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_severity_distribution(self):
        """Returns the count of vulnerabilities grouped by severity (High, Medium, Low)."""
        log = logger.bind(method="get_severity_distribution")
        log.info("query_executing")
        stmt = (
            select(
                Vulnerability.severity,
                func.count(Vulnerability.id).label("count")
            )
            .group_by(Vulnerability.severity)
        ) 
        result = await self.session.execute(stmt)
        data = [
            {"severity": row.severity, "count": row.count} for row in result
        ]
        log.info("query_finished", count=len(data))
        return data

    async def get_top_vulnerable_files(self, limit: int = 10) -> list[dict]:
        """Identifies which files are most frequently flagged for security issues."""
        log = logger.bind(method="get_top_vulnerable_files", limit=limit)
        log.info("query_executing")
        stmt = (
            select(
                Vulnerability.file_path,
                func.count(Vulnerability.id).label("issue_count")
            )
            .group_by(Vulnerability.file_path)
            .order_by(desc("issue_count"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        data = [
            {"file_path": row.file_path, "issue_count": row.issue_count} for row in result
        ]
        log.info("query_finished", count=len(data))
        return data
    
    async def get_summary_stats(self):
        """Returns high-level KPI counts."""
        log = logger.bind(method="get_summary_stats")
        log.info("query_executing")
        total_vulns = await self.session.scalar(select(func.count(Vulnerability.id)))
        total_prs = await self.session.scalar(select(func.count(PullRequest.id)))
        total_repos = await self.session.scalar(select(func.count(Repository.id)))
        open_vulns = await self.session.scalar(
            select(func.count(Vulnerability.id)).where(Vulnerability.status == "open")
        )
        
        stats = {
            "total_vulnerabilities": total_vulns or 0,
            "total_prs_scanned": total_prs or 0,
            "total_repos_monitored": total_repos or 0,
            "open_vulnerabilities": open_vulns or 0
        }
        log.info("query_finished", **stats)
        return stats

    async def get_status_distribution(self):
        """Returns count of vulnerabilities by their status."""
        log = logger.bind(method="get_status_distribution")
        log.info("query_executing")
        stmt = (
            select(Vulnerability.status, func.count(Vulnerability.id).label("count"))
            .group_by(Vulnerability.status)
        )
        result = await self.session.execute(stmt)
        data = [{"status": row.status, "count": row.count} for row in result]
        log.info("query_finished", count=len(data))
        return data

    async def get_vulnerabilities_by_repo(self, limit: int = 5):
        """Returns the most vulnerable repositories."""
        log = logger.bind(method="get_vulnerabilities_by_repo", limit=limit)
        log.info("query_executing")
        stmt = (
            select(Repository.name, func.count(Vulnerability.id).label("count"))
            .join(PullRequest, Repository.id == PullRequest.repository_id)
            .join(Vulnerability, PullRequest.id == Vulnerability.pull_request_id)
            .group_by(Repository.name)
            .order_by(desc("count"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        data = [{"repo_name": row.name, "count": row.count} for row in result]
        log.info("query_finished", count=len(data))
        return data

    async def get_recent_vulnerabilities(self, limit: int = 10):
        """Fetches a feed of the most recent issues for the dashboard."""
        log = logger.bind(method="get_recent_vulnerabilities", limit=limit)
        log.info("query_executing")
        stmt = (
            select(Vulnerability)
            .order_by(desc(Vulnerability.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        data = result.scalars().all()
        log.info("query_finished", count=len(data))
        return data

    async def get_vulnerability_data(self, repository_id: int):
        log = logger.bind(method="get_vulnerability_data", repository_id=repository_id)
        log.info("query_executing")
        stmt = (
            select(Vulnerability)
            .where(Vulnerability.pull_request.has(repository_id=repository_id))
        )
        result = await self.session.execute(stmt)
        data = list(result.scalars().all())
        log.info("query_finished", count=len(data))
        return data
