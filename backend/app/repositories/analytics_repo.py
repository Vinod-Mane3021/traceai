from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.core import Repository, PullRequest, Vulnerability

class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_severity_distribution(self):
        """Returns the count of vulnerabilities grouped by severity (High, Medium, Low)."""
        stmt = (
            select(
                Vulnerability.severity,
                func.count(Vulnerability.id).label("count")
            )
            .group_by(Vulnerability.severity)
        ) 
        result = await self.session.execute(stmt)
        return [
            {"severity": row.severity, "count": row.count} for row in result
        ]

    async def get_top_vulnerable_files(self, limit: int = 10) -> list[dict]:
        """Identifies which files are most frequently flagged for security issues."""
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
        return [
            {"file_path": row.file_path, "issue_count": row.issue_count} for row in result
        ]
    
    async def get_summary_stats(self):
        """Returns high-level KPI counts."""
        total_vulns = await self.session.scalar(select(func.count(Vulnerability.id)))
        total_prs = await self.session.scalar(select(func.count(PullRequest.id)))
        total_repos = await self.session.scalar(select(func.count(Repository.id)))
        open_vulns = await self.session.scalar(
            select(func.count(Vulnerability.id)).where(Vulnerability.status == "open")
        )
        
        return {
            "total_vulnerabilities": total_vulns or 0,
            "total_prs_scanned": total_prs or 0,
            "total_repos_monitored": total_repos or 0,
            "open_vulnerabilities": open_vulns or 0
        }

    async def get_status_distribution(self):
        """Returns count of vulnerabilities by their status."""
        stmt = (
            select(Vulnerability.status, func.count(Vulnerability.id).label("count"))
            .group_by(Vulnerability.status)
        )
        result = await self.session.execute(stmt)
        return [{"status": row.status, "count": row.count} for row in result]

    async def get_vulnerabilities_by_repo(self, limit: int = 5):
        """Returns the most vulnerable repositories."""
        stmt = (
            select(Repository.name, func.count(Vulnerability.id).label("count"))
            .join(PullRequest, Repository.id == PullRequest.repository_id)
            .join(Vulnerability, PullRequest.id == Vulnerability.pull_request_id)
            .group_by(Repository.name)
            .order_by(desc("count"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [{"repo_name": row.name, "count": row.count} for row in result]

    async def get_recent_vulnerabilities(self, limit: int = 10):
        """Fetches a feed of the most recent issues for the dashboard."""
        stmt = (
            select(Vulnerability)
            .order_by(desc(Vulnerability.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()










