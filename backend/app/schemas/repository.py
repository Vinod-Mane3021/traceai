from pydantic import BaseModel, Field


class CreateRepository(BaseModel):
    github_id: int
    name: str
    full_name: str
    organization_id: int
    is_private: bool