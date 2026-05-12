from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from app.schemas.github import GitHubUser

class Permissions(BaseModel):
    contents: str
    metadata: str
    pull_requests: str
    statuses: str

class GitHubAppInstallation(BaseModel):
    id: int
    client_id: str
    account: GitHubUser
    repository_selection: str
    access_tokens_url: str
    repositories_url: str
    html_url: str
    app_id: int
    app_slug: str
    target_id: int
    target_type: str
    permissions: Permissions
    events: List[str]
    created_at: datetime
    updated_at: datetime
    single_file_name: Optional[str] = None
    has_multiple_single_files: bool
    single_file_paths: List[str] = []
    suspended_by: Optional[str] = None
    suspended_at: Optional[datetime] = None

class GitHubAppInstallationRepository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool

class GitHubAppInstallationEventPayload(BaseModel):
    action: str
    installation: GitHubAppInstallation
    repositories: List[GitHubAppInstallationRepository]
    requester: GitHubUser
    sender: GitHubUser

