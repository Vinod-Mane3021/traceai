from fastapi import APIRouter, Depends, HTTPException
import httpx
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

class GitHubCallbackParams(BaseModel):
    code: str

@router.get("/github/callback")
async def github_oauth_callback(payload: GitHubCallbackParams):
    """Exchanges the GitHub OAuth code for an access token and user profile."""
    # 1. Exchange code for GitHub Access Token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": payload.code
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, headers=headers, data=data)
        token_data = token_response.json()

        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error_description"])
        
        access_token = token_data["access_token"]

        # 2. Fetch the user's GitHub Profile
        user_url = "https://api.github.com/user"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = await client.get(user_url, headers=headers)
        user_profile = user_response.json()

    # 3. Create a local JWT for your React frontend (Implementation depends on your auth setup)
    # local_token = create_access_token(data={"sub": user_profile["login"]})

    return {
        "access_token": "YOUR_GENERATED_LOCAL_JWT", # local_token
        "user": {
            "username": user_profile["login"],
            "avatar_url": user_profile["avatar_url"]
        }
    }
