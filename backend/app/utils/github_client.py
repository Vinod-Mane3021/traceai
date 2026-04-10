import httpx
import structlog
from app.utils.github_auth import generate_github_app_jwt

logger = structlog.get_logger(__name__)

class AsyncGithubClient:
    def __init__(self, installation_id:int):
        self.installation_id = installation_id
        self.base_url = "https://api.github.com"
        self.token = None
        self.log = logger.bind(installation_id=installation_id)


    async def _get_installation_token(self) -> str:
        """Exchanges the App JWT for a repository-specific installation token."""
        if self.token:
            return self.token
        
        self.log.info("fetching_installation_token", message="Requesting new installation access token from GitHub")
        app_jwt = generate_github_app_jwt()
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github.v3+json"
        }

        async with httpx.AsyncClient() as client:
            endpoint = f"{self.base_url}/app/installations/{self.installation_id}/access_tokens"
            response = await client.post(endpoint, headers=headers)
            
            if response.status_code != 201:
                self.log.error("installation_token_failed", 
                               message="Failed to fetch installation token",
                               status_code=response.status_code,
                               response=response.text)
            
            response.raise_for_status()
            self.token = response.json()["token"]
            self.log.info("installation_token_success", message="Successfully acquired installation access token")
            return self.token
        
    async def fetch_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetches the raw .diff file for a specific Pull Request."""
        log = self.log.bind(repo=f"{owner}/{repo}", pr_number=pr_number)
        token = await self._get_installation_token()

        # Crucial: The custom Accept header tells GitHub to return raw diff, not JSON metadata
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff"
        }

        log.info("fetching_pr_diff", message=f"Fetching raw diff for PR #{pr_number}")
        async with httpx.AsyncClient() as client:
            endpoint = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = await client.get(endpoint, headers=headers)
            
            if response.status_code != 200:
                log.error("fetch_diff_failed", 
                          message=f"Failed to fetch diff for PR #{pr_number}",
                          status_code=response.status_code)
            
            response.raise_for_status()

            # Returns the raw diff text
            log.info("fetch_diff_success", message=f"Successfully fetched diff for PR #{pr_number}", size=len(response.text))
            return response.text

    async def create_pr_review(self, owner: str, repo: str, pr_number: int, vulnerabilities: list[dict]):
        """
        Creates a PR review with inline comments for each vulnerability.
        """
        log = self.log.bind(repo=f"{owner}/{repo}", pr_number=pr_number)
        token = await self._get_installation_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }

        # Format the AI findings into GitHub's expected comment structure
        comments = []
        for vuln in vulnerabilities:
            # Create a markdown-formatted comment body
            body = f"### 🛡️ Trace AI Security Alert: {vuln['title']}\n"
            body += f"**Severity:** {vuln['severity'].upper()}\n\n"
            body += f"{vuln['description']}"

            comments.append({
                "path": vuln["filename"],
                "line": vuln["line_number"],
                "side": "RIGHT", # Comment on the new code side of the diff
                "body": body
            })

        # The payload for the Review
        payload = {
            "body": "### 🛑 Trace AI Audit Failed\nSecurity vulnerabilities were detected in this Pull Request. Please review the inline comments below.",
            "event": "REQUEST_CHANGES", # This explicitly requests changes, acting as a soft block
            "comments": comments
        }

        log.info("posting_pr_review", message=f"Posting review with {len(comments)} comments to PR #{pr_number}")
        async with httpx.AsyncClient() as client:
            endpoint = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
            response = await client.post(endpoint, headers=headers, json=payload)

            # If a line number is invalid (e.g., AI hallucinated a line not in the diff), 
            # GitHub returns a 422 Unprocessable Entity.
            if response.status_code not in [200, 201]:
                log.error("post_review_failed", 
                          message=f"Failed to post review to PR #{pr_number}",
                          status_code=response.status_code,
                          response=response.text)
            
            response.raise_for_status() 
            log.info("post_review_success", message=f"Successfully posted security review to PR #{pr_number}")

