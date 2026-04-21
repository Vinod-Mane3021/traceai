from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.core import Repository, PullRequest
from app.schemas.github import PullRequestWebhookPayload


class GitHubRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_repo(self, repo_payload) -> Repository:
        """Finds the repo by GitHub ID, or creates it if it's new."""
        result = await self.db.execute(select(Repository).where(Repository.github_id == repo_payload.id))

        repo = result.scalars().first()
        if not repo:
            repo = Repository(
                github_id=repo_payload.id,
                name=repo_payload.name,
                full_name=repo_payload.full_name
            )
            self.db.add(repo)
            await self.db.commit()

        return repo

    async def upsert_pull_request(self, pr_payload, repo_id: int) -> PullRequest:
        """Creates a new PR record or updates the state if it exists."""

        result = await self.db.execute(select(PullRequest).where(PullRequest.github_pr_id == pr_payload.id))

        pr = result.scalars().first()
        if not pr:
            pr = PullRequest(
                github_pr_id=pr_payload.id,
                number=pr_payload.number,
                state=pr_payload.state,
                title=pr_payload.title,
                repository_id=repo_id
            )
            self.db.add(pr)
        else:
            pr.state = pr_payload.state
            pr.title = pr_payload.title
        
        await self.db.commit()

        return pr