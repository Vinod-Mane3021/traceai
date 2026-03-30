from pydantic import BaseModel
from typing import Optional

# We break down the nested JSON into smaller, manageable models
class GitHubUser(BaseModel):
    login: str
    id: int
    avatar_url: str

class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool

class PullRequest(BaseModel):
    id: int
    number: int
    state: str
    title: str
    body: Optional[str] = None
    user: GitHubUser
    diff_url: str  # We will use this later to fetch the code for the AI!

# This is the main payload model GitHub sends for PR events
class PullRequestWebhookPayload(BaseModel):
    action: str  # e.g., "opened", "closed", "synchronize"
    number: int
    pull_request: PullRequest
    repository: Repository