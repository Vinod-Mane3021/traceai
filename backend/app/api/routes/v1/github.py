from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.github_service import list_user_repositories
from app.schemas.github import Repository
from app.api.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/github", tags=["GitHub"])

@router.get("/repositories", response_model=List[Repository])
async def list_repositories(
    installation_id: int = Query(..., description="The GitHub App installation ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetches all repositories accessible to the specified GitHub App installation.
    """
    try:
        repos = await list_user_repositories(installation_id)
        return repos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
