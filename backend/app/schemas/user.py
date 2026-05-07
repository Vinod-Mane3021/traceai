from pydantic import BaseModel
from typing import Optional


class CreateUser(BaseModel):
    username: str
    avatar_url: str
    github_id: int
