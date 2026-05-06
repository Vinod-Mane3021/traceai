from fastapi import APIRouter, HTTPException, status
import httpx
import structlog
from pydantic import BaseModel
from app.core.config import settings
from app.utils.security import create_access_token
from app.repositories.user_repo import UserRepo
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.api.dependencies import get_db
from app.schemas.user import CreateUser



logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

class GitHubCode(BaseModel):
    code: str
    redirect_uri: str | None = None

class AuthUser(BaseModel):
    username: str
    avatar_url: str
    installation_id: int | None = None

class AuthCallbackResponse(BaseModel):
    access_token: str
    user: AuthUser

@router.post("/github/callback", response_model=AuthCallbackResponse)
async def github_oauth_callback(
    payload: GitHubCode,
    db: AsyncSession = Depends(get_db)
):
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

    log.info("exchanging_code_for_token", 
              message="Sending request to GitHub for token exchange", 
              url=token_url,
              client_id=settings.GITHUB_CLIENT_ID,
              has_redirect_uri=bool(payload.redirect_uri))

    async with httpx.AsyncClient() as client:
        try:
            token_response = await client.post(token_url, headers=headers, data=data)
            log.info("github_response_received", 
                      status_code=token_response.status_code,
                      content_preview=token_response.text[:100])
            token_data = token_response.json()
        except Exception as e:
            log.error("github_request_failed", message=str(e))
            raise HTTPException(status_code=500, detail=f"Internal error connecting to GitHub: {str(e)}")

        if "error" in token_data:
            log.error("github_token_exchange_failed", 
                      message="GitHub token exchange failed",
                      error=token_data.get("error"), 
                      description=token_data.get("error_description"),
                      full_response=token_data)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=token_data.get("error_description", "Failed to exchange code for token")
            )
        
        gh_access_token = token_data["access_token"]
        log.info("github_token_received", message="GitHub access token successfully received")

        # 2. Fetch the user's GitHub Profile
        user_url = "https://api.github.com/user"
        user_headers = {"Authorization": f"Bearer {gh_access_token}"}
        
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
        

        # 3. Fetch User's Installations for this App
        # This helps the frontend know which installation to use immediately
        inst_url = "https://api.github.com/user/installations"
        log.debug("fetching_user_installations", message="Fetching app installations for user", url=inst_url)
        inst_response = await client.get(inst_url, headers=user_headers)
        
        installation_id = None
        if inst_response.status_code == 200:
            inst_data = inst_response.json()
            installations = inst_data.get("installations", [])
            if installations:
                # For simplicity in this demo, we take the first active installation
                installation_id = installations[0].get("id")
                log.info("user_installation_found", 
                         installation_id=installation_id, 
                         count=len(installations))
        else:
            log.warning("user_installations_fetch_failed", 
                        status_code=inst_response.status_code,
                        response=inst_response.text)
            
    # create user into database
    user_repo = UserRepo(db)
    user = CreateUser(
        avatar_url=user_data["avatar_url"],
        github_id=user_data["id"],
        username=user_data["login"],
        installation_id=installation_id
    )
    await user_repo.create_user_if_not_exists(user_data=user)
    

    # 4. Create a local JWT for the frontend
    local_token = create_access_token(data={"sub": user_data["login"], "sub_github_id": user_data["id"]})
    log.info("local_jwt_generated", 
             message="Local session JWT generated for user",
             username=user_data.get("login"))

    return {
        "access_token": local_token,
        "user": {
            "username": user_data["login"],
            "avatar_url": user_data["avatar_url"],
            "installation_id": installation_id
        }
    }
