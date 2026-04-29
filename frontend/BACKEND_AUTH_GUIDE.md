export const env = {
  appName: import.meta.env.VITE_APP_NAME ?? "App",
  appDescription: import.meta.env.VITE_APP_DESCRIPTION ?? "",
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api",
  mockApi: String(import.meta.env.VITE_MOCK_API_CALLS).toLowerCase() === "true",
};
ode` to your FastAPI backend.
4.  **Token Exchange (Backend)**: Backend exchanges `code` for a GitHub `access_token`.
5.  **User Info (Backend)**: Backend fetches user details from GitHub using the token.
6.  **Response**: Backend returns a session token (JWT) and user details to the frontend.

---

## 2. API Specifications

### Endpoint: `POST /v1/auth/github/callback`

> **Note**: Your current frontend implementation uses `GET` with a JSON body in `use-github-callback.ts`. This is non-standard. We recommend changing it to `POST`.

**Request Body**
```json
{
  "code": "string"
}
```

**Response Body (`AuthCallbackResponse`)**
```json
{
  "access_token": "string",
  "user": {
    "username": "string",
    "avatar_url": "string"
  }
}
```

---

## 3. FastAPI Implementation

### Requirements
```bash
pip install fastapi uvicorn pydantic httpx python-jose[cryptography]
```

### Models (`schemas.py`)
```python
from pydantic import BaseModel

class AuthUser(BaseModel):
    username: string
    avatar_url: string

class AuthCallbackResponse(BaseModel):
    access_token: str
    user: AuthUser

class GitHubCode(BaseModel):
    code: str
```

### Implementation (`main.py`)
```python
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import GitHubCode, AuthCallbackResponse, AuthUser

app = FastAPI()

# Add CORS Middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_CLIENT_ID = "your_client_id"
GITHUB_CLIENT_SECRET = "your_client_secret"

# Matches your current logs showing /api/v1/...
@app.post("/api/v1/auth/github/callback", response_model=AuthCallbackResponse)
async def github_callback(payload: GitHubCode):
    # 1. Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            params={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": payload.code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_res.json()
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error_description"])
            
        gh_access_token = token_data["access_token"]

        # 2. Get user info from GitHub
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {gh_access_token}"},
        )
        user_data = user_res.json()
        
    # 3. Create your own JWT or session token here
    return {
        "access_token": f"session_{gh_access_token[:10]}",
        "user": {
            "username": user_data["login"],
            "avatar_url": user_data["avatar_url"]
        }
    }
```

---

## 4. Required Frontend Change

In `src/features/auth/api/use-github-callback.ts`, update the `exchangeCode` function to use `POST`:

```typescript
async function exchangeCode(code: string): Promise<AuthCallbackResponse> {
  // ...
  return apiRequest<AuthCallbackResponse>("/v1/auth/github/callback", {
    method: "POST", // Changed from GET
    body: JSON.stringify({ code }),
  });
}
```

## 5. Environment Variables

Ensure your backend has access to:
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`

These must match the ones used in your GitHub OAuth Application settings.
