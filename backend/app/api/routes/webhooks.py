from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.github_service import process_pull_request_event
from app.utils.security import verify_github_signature
from app.schemas.github import PullRequestWebhookPayload

router = APIRouter()

@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    # 1. Verify it is actually from GitHub
    await verify_github_signature(request, x_hub_signature_256)

    # 2. Handle the Ping event to verify the connection
    if x_github_event == "ping":
        print("🏓 GitHub sent a ping event! Connection successful.")
        return {"status": "accepted", "message": "Ping received"}
    
    # 4. Handle PR events with Pydantic Validation
    if x_github_event == "pull_request":
        # Parse the raw JSON body
        try:
            row_payload = await request.json()
            print(f"DEBUG: Payload action: {row_payload.get('action')}")
        except Exception as e:
            print(f"❌ Failed to parse JSON body: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        try:
            # We parse the raw JSON body into our strict Pydantic model
            payload = PullRequestWebhookPayload(**row_payload)
        except Exception as e:
            print(f"❌ Pydantic validation failed: {e}")
            # print(f"DEBUG: row_payload was: {row_payload}")
            raise HTTPException(status_code=422, detail="Invalid payload structure")

        try:
            # Pass the validated payload and the DB session to the service layer
            print(f"DEBUG: Starting process_pull_request_event for PR #{payload.number}")
            await process_pull_request_event(payload, db)
            print(f"DEBUG: Finished process_pull_request_event for PR #{payload.number}")

            print(f"📦 PR #{payload.number} '{payload.action}' by {payload.pull_request.user.login}")
            print(f"Repo: {payload.repository.full_name}")
            print(f"Diff URL ready for AI: {payload.pull_request.diff_url}")

        except Exception as e:
            import traceback
            print(f"❌ Error processing payload: {type(e).__name__}: {e}")
            traceback.print_exc()
            # Log the error and return a 500 since this is an internal failure, not a validation failure
            raise HTTPException(status_code=500, detail=f"Internal server error: {type(e).__name__}")
    
    return {"status": "accepted", "message": "PR event received"}