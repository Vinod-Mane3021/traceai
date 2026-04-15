import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session_maker
from app.repositories.analytics_repo import AnalyticsRepository

async def test_analytics():
    async with async_session_maker() as session:
        repo = AnalyticsRepository(session)
        
        print("\n--- Severity Distribution ---")
        severity_dist = await repo.get_severity_distribution()
        for item in severity_dist:
            print(f"{item['severity']}: {item['count']}")
            
        print("\n--- Top Vulnerable Files ---")
        top_files = await repo.get_top_vulnerable_files()
        for item in top_files:
            print(f"{item['file_path']}: {item['issue_count']}")
            
        print("\n--- Recent Vulnerabilities (Feed) ---")
        recent = await repo.get_recent_vulnerabilities(limit=5)
        for vuln in recent:
            print(f"[{vuln.severity}] {vuln.file_path} (ID: {vuln.id})")

if __name__ == "__main__":
    asyncio.run(test_analytics())
