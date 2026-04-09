from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.github import PullRequestWebhookPayload
from app.repositories.github_repo import GitHubRepository
from app.utils.github_client import AsyncGithubClient

async def process_pull_request_event(payload: PullRequestWebhookPayload, db: AsyncSession):
    """Core business logic for handling incoming PRs."""
    
    # 1. Extract metadata from your Pydantic validated payload
    installation_id = payload.installation.id
    owner = payload.repository.owner.login
    repo_name = payload.repository.name
    pr_number = payload.pull_request.number


    
    repo_payer = GitHubRepository(db)

    # 2. Ensure the repository exists in our database
    db_repo = await repo_payer.get_or_create_repo(payload.repository)

    # 3. Save or update the Pull Request details
    db_pr = await repo_payer.upsert_pull_request(payload.pull_request, db_repo.id)

    print(f"✅ Successfully saved PR #{db_pr.number} ({db_pr.state}) to the database!")

    # 4. Fetch the actual code diff
    try:
        github_client = AsyncGithubClient(installation_id=installation_id)
        raw_diff = await github_client.fetch_pr_diff(
            owner=owner, 
            repo=repo_name, 
            pr_number=pr_number
        )
        print(f"Successfully fetched diff for PR #{pr_number}. Length: {len(raw_diff)} characters.")
        print(raw_diff)
        # TODO: The next step will be passing this 'raw_diff' to the chunking/AI service.
    except Exception as e:
        print(f"❌ Failed to fetch PR diff: {type(e).__name__}: {e}")
        # Here you would typically log the error and maybe update the PR status to 'errored'
        # We can choose to either fail silently here or raise an exception depending on how critical this is
        # For now, let's just log the error and continueAsyncGitHubClient without the diff

    return db_pr
    