import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.github import PullRequestWebhookPayload
from app.repositories.github_repo import GitHubRepository
from app.utils.diff_processor import parse_and_filter_diff
from app.utils.github_client import AsyncGithubClient
from app.services.ai_service import analyze_code_chunk

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
        
        # 5. Filter and Chunk the Diff
        chunks = parse_and_filter_diff(raw_diff)
        print(f"Found {len(chunks)} analyzable files in PR #{pr_number}")

        # 6. Analyze all chunks concurrently
        # This fires off all API calls to liteLLM provider at the exact same time!
        tasks = [
            analyze_code_chunk(chunk["filename"], chunk["content"]) for chunk in chunks
        ]
        ai_results = await asyncio.gather(*tasks)

        # 7. Aggregate the findings
        all_vulnerabilities = []
        for result in ai_results:
            all_vulnerabilities.extend(result.get("vulnerabilities", []))

        print(f"Analysis Complete! Found {len(all_vulnerabilities)} total vulnerabilities.")

        # 8. Post the Inline Review if vulnerabilities exist
        if all_vulnerabilities:
            print(f"Vulnerabilities found: {len(all_vulnerabilities)}")
            print("Posting inline review to GitHub...")
            try:
                await github_client.create_pr_review(
                    owner=owner,
                    repo=repo_name,
                    pr_number=pr_number,
                    vulnerabilities=all_vulnerabilities
                )
                print("Successfully posted security review.")
            except Exception as e:
                print(f"❌ Failed to post review: {type(e).__name__}: {e}")
        else:
            print("No vulnerabilities found. Code looks secure.")

    except Exception as e:
        print(f"❌ Failed to fetch PR diff: {type(e).__name__}: {e}")
        # Here you would typically log the error and maybe update the PR status to 'errored'
        # We can choose to either fail silently here or raise an exception depending on how critical this is
        # For now, let's just log the error and continueAsyncGitHubClient without the diff

    return db_pr
    