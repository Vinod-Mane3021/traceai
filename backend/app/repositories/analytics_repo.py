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

    async def get_top_vulnerable_files(self, limit: int = 10):
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
    
    async def get_recent_vulnerabilities(self, limit: int = 10):
        """Fetches a feed of the most recent issues for the dashboard."""
        stmt = (
            select(Vulnerability)
            .order_by(desc(Vulnerability.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()










