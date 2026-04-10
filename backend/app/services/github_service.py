import asyncio
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.github import PullRequestWebhookPayload
from app.repositories.github_repo import GitHubRepository
from app.utils.diff_processor import parse_and_filter_diff
from app.utils.github_client import AsyncGithubClient
from app.services.ai_service import analyze_code_chunk

logger = structlog.get_logger(__name__)

async def process_pull_request_event(payload: PullRequestWebhookPayload, db: AsyncSession):
    """Core business logic for handling incoming PRs."""
    
    # 1. Extract metadata from your Pydantic validated payload
    installation_id = payload.installation.id
    owner = payload.repository.owner.login
    repo_name = payload.repository.name
    pr_number = payload.pull_request.number

    # Bind common context to all logs in this function
    log = logger.bind(
        repo=f"{owner}/{repo_name}",
        pr_number=pr_number,
        installation_id=installation_id
    )

    repo_payer = GitHubRepository(db)

    # 2. Ensure the repository exists in our database
    db_repo = await repo_payer.get_or_create_repo(payload.repository)

    # 3. Save or update the Pull Request details
    db_pr = await repo_payer.upsert_pull_request(payload.pull_request, db_repo.id)

    log.info("pr_saved_to_db", message=f"PR #{pr_number} successfully saved to database", state=db_pr.state)

    # 4. Fetch the actual code diff
    try:
        github_client = AsyncGithubClient(installation_id=installation_id)
        raw_diff = await github_client.fetch_pr_diff(
            owner=owner, 
            repo=repo_name, 
            pr_number=pr_number
        )
        log.info("diff_fetched", message=f"Successfully fetched diff for PR #{pr_number}", diff_length=len(raw_diff))
        
        # 5. Filter and Chunk the Diff
        chunks = parse_and_filter_diff(raw_diff)
        log.info("diff_chunked", message=f"Split diff into {len(chunks)} analyzable chunks", chunk_count=len(chunks))

        # 6. Analyze all chunks concurrently
        if chunks:
            log.info("ai_analysis_start", message=f"Starting AI analysis for {len(chunks)} chunks", task_count=len(chunks))
            tasks = [
                analyze_code_chunk(chunk["filename"], chunk["content"]) for chunk in chunks
            ]
            ai_results = await asyncio.gather(*tasks)

            # 7. Aggregate the findings
            all_vulnerabilities = []
            for result in ai_results:
                all_vulnerabilities.extend(result.get("vulnerabilities", []))

            log.info("ai_analysis_complete", message=f"AI analysis finished. Found {len(all_vulnerabilities)} vulnerabilities", vulnerability_count=len(all_vulnerabilities))

            # 8. Post the Inline Review if vulnerabilities exist
            if all_vulnerabilities:
                log.info("posting_github_review", message=f"Posting review with {len(all_vulnerabilities)} findings to GitHub", count=len(all_vulnerabilities))
                try:
                    await github_client.create_pr_review(
                        owner=owner,
                        repo=repo_name,
                        pr_number=pr_number,
                        vulnerabilities=all_vulnerabilities
                    )
                    log.info("github_review_posted_success", message="Security review successfully posted to GitHub")
                except Exception as e:
                    log.error("github_review_posted_failed", message="Failed to post security review to GitHub", error=str(e), error_type=type(e).__name__)
            else:
                log.info("no_vulnerabilities_found", message="No vulnerabilities found. Code looks secure.")
        else:
            log.info("no_analyzable_chunks_found", message="No analyzable files found in this PR.")

    except Exception as e:
        log.error("process_pr_event_failed", message="Critical error processing PR event", error=str(e), error_type=type(e).__name__)
        # Here you would typically update the PR status in the DB to 'errored'

    return db_pr
    