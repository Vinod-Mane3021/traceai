from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.github import PullRequestWebhookPayload
from app.repositories.github_repo import GitHubRepository

async def process_pull_request_event(payload: PullRequestWebhookPayload, db: AsyncSession):
    """Core business logic for handling incoming PRs."""
    repo_payer = GitHubRepository(db)

    # 1. Ensure the repository exists in our database
    db_repo = await repo_payer.get_or_create_repo(payload.repository)

    # 2. Save or update the Pull Request details
    db_pr = await repo_payer.upsert_pull_request(payload.pull_request, db_repo.id)

    print(f"✅ Successfully saved PR #{db_pr.number} ({db_pr.state}) to the database!")

    # Next phase: Trigger the AI code analysis here using db_pr.diff_url

    return db_pr