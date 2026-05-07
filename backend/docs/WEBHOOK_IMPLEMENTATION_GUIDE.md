# Guide: Implementing the GitHub Installation Webhook

## 1. Overview
The `installation` webhook is critical for multi-tenancy. It allows the application to automatically create and manage "Organizations" (Tenants) when the GitHub App is installed. This guide explains how to implement this in the current FastAPI/SQLAlchemy stack.

---

## 2. Step 1: Update Pydantic Schemas (`app/schemas/github.py`)
You need a model to validate the incoming `installation` event payload.

```python
class InstallationAccount(BaseModel):
    login: str
    id: int
    type: str  # "Organization" or "User"

class InstallationEvent(BaseModel):
    action: str  # "created", "deleted", "suspend", "unsuspend"
    installation: Installation
    repositories: Optional[List[Repository]] = []
    sender: GitHubUser

    class Config:
        extra = "ignore"
```

---

## 3. Step 2: Create the Service Logic (`app/services/organization_service.py`)
Create a new service to handle the business logic of creating organizations and members.

```python
async def handle_installation_event(payload: InstallationEvent, db: AsyncSession):
    action = payload.action
    inst_id = payload.installation.id
    
    if action == "created":
        # 1. Create Organization
        org = await org_repo.create_org(
            name=payload.installation.account.login,
            github_id=inst_id,
            type=payload.installation.account.type
        )
        
        # 2. Sync initial repositories
        for repo_data in payload.repositories:
            await repo_repo.create_repo(org.id, repo_data)
            
    elif action == "deleted":
        await org_repo.deactivate_org(inst_id)
```

---

## 4. Step 3: Update the Webhook Router (`app/api/routes/v1/webhooks.py`)
Modify the router to switch between `pull_request` and `installation` events.

```python
@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # ... Signature Verification ...

    if x_github_event == "installation":
        raw_payload = await request.json()
        payload = InstallationEvent(**raw_payload)
        await handle_installation_event(payload, db)
        return {"status": "success", "message": "Installation processed"}

    if x_github_event == "pull_request":
        # ... existing PR logic ...
```

---

## 5. Step 4: Local Testing
You can't easily trigger a real GitHub webhook on localhost. Use a tool like **`curl`** or **Postman** to send a dummy JSON payload to your endpoint:

### Dummy `created` Payload:
```json
{
  "action": "created",
  "installation": {
    "id": 12345,
    "account": {
      "login": "AcmeCorp",
      "type": "Organization"
    }
  },
  "repositories": [
    { "id": 6789, "name": "web-app", "full_name": "AcmeCorp/web-app" }
  ],
  "sender": { "login": "admin-user", "id": 1 }
}
```

### How to test:
1.  Run your server (`uvicorn app.main:app`).
2.  Send the JSON above via POST to `http://localhost:8000/api/v1/webhooks/github`.
3.  Include the header `X-GitHub-Event: installation`.
4.  Verify in your database that a new row appeared in the `organizations` table.

---

## 6. Security Note
Always ensure that `verify_github_signature` is active, even for the installation webhook, to prevent malicious actors from creating fake organizations in your database.
