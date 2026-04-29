from fastapi import APIRouter, HTTPException, status
import httpx
import structlog
from pydantic import BaseModel
from app.core.config import settings
from app.utils.security import create_access_token

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class GitHubCode(BaseModel):
    code: str
    redirect_uri: str | None = None

class AuthUser(BaseModel):
    username: str
    avatar_url: str

class AuthCallbackResponse(BaseModel):
    access_token: str
    user: AuthUser

@router.post("/github/callback", response_model=AuthCallbackResponse)
async def github_oauth_callback(payload: GitHubCode):
    """Exchanges the GitHub OAuth code for an access token and user profile."""
    log = logger.bind(auth_flow="github_oauth")
    log.info("auth_callback_received", 
             message="GitHub OAuth callback received with code", 
             code_preview=f"{payload.code[:5]}...")
    
    # 1. Exchange code for GitHub Access Token
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": payload.code
    }
    if payload.redirect_uri:
        data["redirect_uri"] = payload.redirect_uri

    async with httpx.AsyncClient() as client:
        log.debug("exchanging_code_for_token", message="Exchanging code for GitHub access token", url=token_url)
        token_response = await client.post(token_url, headers=headers, data=data)
        token_data = token_response.json()

        if "error" in token_data:
            log.error("github_token_exchange_failed", 
                      message="GitHub token exchange failed",
                      error=token_data.get("error"), 
                      description=token_data.get("error_description"))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=token_data.get("error_description", "Failed to exchange code for token")
            )
        
        gh_access_token = token_data["access_token"]
        log.info("github_token_received", message="GitHub access token successfully received")

        # 2. Fetch the user's GitHub Profile
        user_url = "https://api.github.com/user"
        user_headers = {"Authorization": f"token {gh_access_token}"}
        
        log.debug("fetching_github_profile", message="Fetching user profile from GitHub", url=user_url)
        user_response = await client.get(user_url, headers=user_headers)
        
        if user_response.status_code != 200:
            log.error("github_profile_fetch_failed", 
                      message="Failed to fetch GitHub user profile",
                      status_code=user_response.status_code)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to fetch user profile from GitHub"
            )
            
        user_data = user_response.json()
        log.info("github_profile_received", 
                 message="GitHub user profile successfully retrieved",
                 username=user_data.get("login"))

    # 3. Create a local JWT for the React frontend
    local_token = create_access_token(data={"sub": user_data["login"]})
    log.info("local_jwt_generated", 
             message="Local session JWT generated for user",
             username=user_data.get("login"))

    return {
        "access_token": local_token,
        "user": {
            "username": user_data["login"],
            "avatar_url": user_data["avatar_url"]
        }
    }
