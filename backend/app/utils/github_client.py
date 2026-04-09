import httpx
from app.utils.github_auth import generate_github_app_jwt

class AsyncGithubClient:
    def __init__(self, installation_id:int):
        self.installation_id = installation_id
        self.base_url = "https://api.github.com"
        self.token = None


    async def _get_installation_token(self) -> str:
        """Exchanges the App JWT for a repository-specific installation token."""
        if self.token:
            return self.token
        
        app_jwt = generate_github_app_jwt()
        headers = {
            "Authorization": f"Bearer {app_jwt}",
            "Accept": "application/vnd.github.v3+json"
        }

        async with httpx.AsyncClient() as client:
            endpoint = f"{self.base_url}/app/installations/{self.installation_id}/access_tokens"
            response = await client.post(endpoint, headers=headers)
            response.raise_for_status()
            self.token = response.json()["token"]
            return self.token
        
    async def fetch_pr_diff(self, owner: str, repo: str, pr_number: int) -> str:
        """Fetches the raw .diff file for a specific Pull Request."""
        token = await self._get_installation_token()

        # Crucial: The custom Accept header tells GitHub to return raw diff, not JSON metadata
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.diff"
        }

        async with httpx.AsyncClient() as client:
            endpoint = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            response = await client.get(endpoint, headers=headers)
            response.raise_for_status()

            # Returns the raw diff text
            return response.text



