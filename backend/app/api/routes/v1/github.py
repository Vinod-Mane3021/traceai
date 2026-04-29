from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.github_service import list_user_repositories
from app.schemas.github import Repository
from app.api.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/github", tags=["GitHub"])

@router.get("/repositories", response_model=List[Repository])
async def list_repositories(
    installation_id: str | None = Query(None, description="The GitHub App installation ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetches all repositories accessible to the specified GitHub App installation.
    """
    if not installation_id or installation_id == "demo":
        raise HTTPException(
            status_code=400, 
            detail="Valid installation_id is required. Please install the GitHub App first."
        )
    
    try:
        # Convert to int after manual check to provide better error if it's not a number
        try:
            inst_id_int = int(installation_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="installation_id must be a valid integer.")
            
        repos = await list_user_repositories(inst_id_int)
        return repos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
