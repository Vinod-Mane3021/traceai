from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.models.core import Repository
from app.schemas.repository import CreateRepository

class RepositoryRepo:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def upsert_repository(self, repo_data: CreateRepository) -> Repository:
        """Finds the repository by GitHub ID, or creates it if it's new."""
        result = self.db.execute(select(Repository).where(Repository.github_id == repo_data.github_id))

        repo = result.scalars().first()
        if not repo:
            repo = Repository(
                github_id=repo_data.github_id,
                name=repo_data.name,
                full_name=repo_data.full_name,
                is_private=repo_data.is_private,
                organization_id=repo_data.organization_id,
            )
            self.db.add(repo)
            self.db.commit()

        return repo
        
    async def upsert_repositories_bulk(self, repositories: list[CreateRepository]) -> list[Repository]:
        """Bulk upsert repositories."""
        # This is a simplified example. In production, you might want to use more efficient bulk operations.
        upserted_repos = []
        for repo in repositories:
            upserted_repo = await self.upsert_repository(
                github_id=repo.github_id,
                name=repo.name,
                full_name=repo.full_name,
                organization_id=repo.organization_id,
                is_private=repo.is_private,
            )
            upserted_repos.append(upserted_repo)
        return upserted_repos