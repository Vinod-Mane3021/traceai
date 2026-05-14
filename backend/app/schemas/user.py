from pydantic import BaseModel
from typing import Optional


class CreateUser(BaseModel):
    username: str
    avatar_url: str
    github_id: int


class UpdateUser(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    github_id: Optional[int] = None
    last_active_org_id: Optional[int] = None