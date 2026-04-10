import asyncio
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.github import PullRequestWebhookPayload
from app.repositories.github_repo import GitHubRepository
from app.utils.diff_processor import parse_and_filter_diff
from app.utils.github_client import AsyncGithubClient
from app.services.ai_service import analyze_code_chunk

logger = structlog.get_logger(__name__)

async def _set_initial_commit_status(github_client: AsyncGithubClient, owner: str, repo_name: str, head_sha: str, log: structlog.BoundLogger) -> None:
    """
    Sets the initial commit status to 'pending' to block early merges.
    This indicates that the Trace AI scan is currently in progress.
    """
    try:
        await github_client.set_commit_status(
            owner=owner,
            repo=repo_name,
            sha=head_sha,
            state="pending",
            description="Trace AI is scanning for vulnerabilities..."
        )
        log.info("initial_status_set", message="Set initial commit status to 'pending'")
    except Exception as e:
        log.error("initial_status_set_failed", message="Failed to set initial commit status", error=str(e), error_type=type(e).__name__)

async def _sync_pr_to_db(payload: PullRequestWebhookPayload, db: AsyncSession, log: structlog.BoundLogger):
    """
    Ensures the repository exists in our database and upserts the Pull Request details.
    Returns the saved Pull Request database object.
    """
    repo_payer = GitHubRepository(db)
    
    # Ensure the repository exists in our database
    db_repo = await repo_payer.get_or_create_repo(payload.repository)
    
    # Save or update the Pull Request details
    db_pr = await repo_payer.upsert_pull_request(payload.pull_request, db_repo.id)
    log.info("pr_saved_to_db", message=f"PR #{payload.pull_request.number} successfully saved to database", state=db_pr.state)
    
    return db_pr

async def _analyze_pr_diff(github_client: AsyncGithubClient, owner: str, repo_name: str, pr_number: int, log: structlog.BoundLogger) -> list[dict]:
    """
    Fetches the PR diff, filters it into chunks, and processes each chunk concurrently using AI.
    Returns a combined list of all discovered vulnerabilities.
    """
    raw_diff = await github_client.fetch_pr_diff(owner=owner, repo=repo_name, pr_number=pr_number)
    log.info("diff_fetched", message=f"Successfully fetched diff for PR #{pr_number}", diff_length=len(raw_diff))
    
    chunks = parse_and_filter_diff(raw_diff)
    all_vulnerabilities = []

    if not chunks:
        log.info("no_analyzable_chunks_found", message="No analyzable files found in this PR.")
        return all_vulnerabilities

    log.info("diff_chunked", message=f"Split diff into {len(chunks)} analyzable chunks", chunk_count=len(chunks))
    log.info("ai_analysis_start", message=f"Starting AI analysis for {len(chunks)} chunks", task_count=len(chunks))
    
    # Analyze all chunks concurrently
    tasks = [analyze_code_chunk(chunk["filename"], chunk["content"]) for chunk in chunks]
    ai_results = await asyncio.gather(*tasks)

    # Aggregate the findings
    for result in ai_results:
        all_vulnerabilities.extend(result.get("vulnerabilities", []))

    log.info("ai_analysis_complete", message=f"AI analysis finished. Found {len(all_vulnerabilities)} vulnerabilities", vulnerability_count=len(all_vulnerabilities))
    
    return all_vulnerabilities

async def _report_analysis_results(github_client: AsyncGithubClient, owner: str, repo_name: str, pr_number: int, head_sha: str, vulnerabilities: list[dict], log: structlog.BoundLogger) -> None:
    """
    Sets the final commit status and posts an inline review if vulnerabilities are detected.
    If the code is secure, sets the commit status to success.
    """
    if vulnerabilities:
        log.info("vulnerabilities_found", message=f"Vulnerabilities detected in PR #{pr_number}. Blocking merge and posting review.", vulnerability_count=len(vulnerabilities))
        
        # Block the merge with a failure status
        log.info("setting_commit_status_failure", message="Setting commit status to 'failure' due to detected vulnerabilities")
        await github_client.set_commit_status(
            owner=owner, repo=repo_name, sha=head_sha,
            state="failure", description=f"Blocked: Found {len(vulnerabilities)} security issues."
        )

        # Post the inline review comments
        log.info("posting_github_review", message="Posting security review to GitHub")
        try:
            await github_client.create_pr_review(
                owner=owner, repo=repo_name, pr_number=pr_number,
                vulnerabilities=vulnerabilities
            )
            log.info("github_review_posted_success", message="Security review successfully posted to GitHub")
        except Exception as e:
            log.error("github_review_posted_failed", message="Failed to post security review to GitHub", error=str(e), error_type=type(e).__name__)
    else:
        log.info("no_vulnerabilities_found", message="No vulnerabilities found. Code looks secure. Unlocking merge...")
        
        # Unblock the merge with a success status
        await github_client.set_commit_status(
            owner=owner, repo=repo_name, sha=head_sha,
            state="success", description="Passed: No vulnerabilities detected, safe to merge."
        )

async def process_pull_request_event(payload: PullRequestWebhookPayload, db: AsyncSession):
    """
    Core business logic for handling incoming PR webhook events.
    Delegates tasks to specialized helper functions for better readability.
    """
    
    # Extract metadata from the Pydantic validated payload
    installation_id = payload.installation.id
    owner = payload.repository.owner.login
    repo_name = payload.repository.name
    pr_number = payload.pull_request.number
    head_sha = payload.pull_request.head.sha

    # Bind common context to all logs in this function
    log = logger.bind(
        repo=f"{owner}/{repo_name}",
        pr_number=pr_number,
        installation_id=installation_id
    )

    github_client = AsyncGithubClient(installation_id=installation_id)

    # IMMEDIATELY set the status to "pending" to block early merges
    await _set_initial_commit_status(github_client, owner, repo_name, head_sha, log)
    
    # Sync repository and PR metadata into the database
    db_pr = await _sync_pr_to_db(payload, db, log)

    try:
        # Analyze code for vulnerabilities and update GitHub statuses/reviews accordingly
        vulnerabilities = await _analyze_pr_diff(github_client, owner, repo_name, pr_number, log)
        await _report_analysis_results(github_client, owner, repo_name, pr_number, head_sha, vulnerabilities, log)
        
    except Exception as e:
        log.error("process_pr_event_failed", message="Critical error processing PR event", error=str(e), error_type=type(e).__name__)
        # Here you would typically update the PR status in the DB to 'errored'

    return db_pr
    