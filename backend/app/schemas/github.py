from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime

class GitHubUser(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: Optional[str]
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    user_view_type: str
    site_admin: bool

class Repository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: GitHubUser
    html_url: str
    description: Optional[str]
    fork: bool
    url: str
    forks_url: str
    keys_url: str
    collaborators_url: str
    teams_url: str
    hooks_url: str
    issue_events_url: str
    events_url: str
    assignees_url: str
    branches_url: str
    tags_url: str
    blobs_url: str
    git_tags_url: str
    git_refs_url: str
    trees_url: str
    statuses_url: str
    languages_url: str
    stargazers_url: str
    contributors_url: str
    subscribers_url: str
    subscription_url: str
    commits_url: str
    git_commits_url: str
    comments_url: str
    issue_comment_url: str
    contents_url: str
    compare_url: str
    merges_url: str
    archive_url: str
    downloads_url: str
    issues_url: str
    pulls_url: str
    milestones_url: str
    notifications_url: str
    labels_url: str
    releases_url: str
    deployments_url: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: Optional[str]
    size: int
    stargazers_count: int
    watchers_count: int
    language: Optional[str]
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    has_discussions: bool
    forks_count: int
    mirror_url: Optional[str]
    archived: bool
    disabled: bool
    open_issues_count: int
    license: Optional[Any]
    allow_forking: bool
    is_template: bool
    web_commit_signoff_required: bool
    has_pull_requests: bool
    pull_request_creation_policy: Optional[str] = None
    topics: List[str]
    visibility: str
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    
    # These fields appear specifically in the head/base repo blocks
    allow_squash_merge: Optional[bool] = None
    allow_merge_commit: Optional[bool] = None
    allow_rebase_merge: Optional[bool] = None
    allow_auto_merge: Optional[bool] = None
    delete_branch_on_merge: Optional[bool] = None
    allow_update_branch: Optional[bool] = None
    use_squash_pr_title_as_default: Optional[bool] = None
    squash_merge_commit_message: Optional[str] = None
    squash_merge_commit_title: Optional[str] = None
    merge_commit_message: Optional[str] = None
    merge_commit_title: Optional[str] = None

class BranchInfo(BaseModel):
    label: str
    ref: str
    sha: str
    user: GitHubUser
    repo: Repository

class Link(BaseModel):
    href: str

class PRLinks(BaseModel):
    self: Link
    html: Link
    issue: Link
    comments: Link
    review_comments: Link
    review_comment: Link
    commits: Link
    statuses: Link

class PullRequest(BaseModel):
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: GitHubUser
    body: Optional[str]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]
    merged_at: Optional[datetime]
    merge_commit_sha: Optional[str]
    assignees: List[Any]
    requested_reviewers: List[Any]
    requested_teams: List[Any]
    labels: List[Any]
    milestone: Optional[Any]
    draft: bool
    commits_url: str
    review_comments_url: str
    review_comment_url: str
    comments_url: str
    statuses_url: str
    head: BranchInfo
    base: BranchInfo
    links: PRLinks = Field(alias="_links")  # Maps JSON '_links' to Python 'links'
    author_association: str
    auto_merge: Optional[Any]
    assignee: Optional[Any]
    active_lock_reason: Optional[Any]
    merged: bool
    mergeable: Optional[bool]
    rebaseable: Optional[bool]
    mergeable_state: str
    merged_by: Optional[GitHubUser]
    comments: int
    review_comments: int
    maintainer_can_modify: bool
    commits: int
    additions: int
    deletions: int
    changed_files: int

class Installation(BaseModel):
    id: int
    node_id: str

# Main payload model
class PullRequestWebhookPayload(BaseModel):
    action: str
    number: int
    pull_request: PullRequest
    repository: Repository
    sender: GitHubUser
    installation: Installation

    
# from pydantic import BaseModel
# from typing import Optional

# # We break down the nested JSON into smaller, manageable models
# class GitHubUser(BaseModel):
#     login: str
#     id: int
#     avatar_url: str

# class Repository(BaseModel):
#     id: int
#     name: str
#     full_name: str
#     private: bool
#     owner: GitHubUser


# class PullRequest(BaseModel):
#     id: int
#     number: int
#     state: str
#     title: str
#     body: Optional[str] = None
#     user: GitHubUser
#     diff_url: str  # We will use this later to fetch the code for the AI!

# class Installation(BaseModel):
#     id: int
#     node_id: str

# # This is the main payload model GitHub sends for PR events
# class PullRequestWebhookPayload(BaseModel):
#     action: str  # e.g., "opened", "closed", "synchronize"
#     number: int
#     pull_request: PullRequest
#     repository: Repository
#     installation: Installation