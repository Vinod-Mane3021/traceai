from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import traceback

from app.api.dependencies import get_db
from app.services.github_service import process_pull_request_event
from app.utils.security import verify_github_signature
from app.schemas.github import PullRequestWebhookPayload

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])
logger = structlog.get_logger(__name__)

@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    log = logger.bind(event_type=x_github_event)

    # 1. Verify it is actually from GitHub
    await verify_github_signature(request, x_hub_signature_256)

    # 2. Handle the Ping event to verify the connection
    if x_github_event == "ping":
        log.info("github_ping_received", message="GitHub sent a ping event! Connection successful.")
        return {"status": "accepted", "message": "Ping received"}

    # 4. Handle PR events with Pydantic Validation
    if x_github_event == "pull_request":
        # Parse the raw JSON body
        try:
            row_payload = await request.json()
            log = log.bind(action=row_payload.get("action"))
        except Exception as e:
            log.error("json_parse_failed", message="Failed to parse JSON body from webhook", error=str(e))
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        try:
            # We parse the raw JSON body into our strict Pydantic model
            payload = PullRequestWebhookPayload(**row_payload)
            log = log.bind(pr_number=payload.number, repo=payload.repository.full_name)
        except Exception as e:
            log.error("pydantic_validation_failed", message="Payload failed Pydantic validation", error=str(e))
            raise HTTPException(status_code=422, detail="Invalid payload structure")

        try:
            # Pass the validated payload and the DB session to the service layer
            log.info("processing_pr_event_start", message=f"Starting processing for PR #{payload.number}")
            await process_pull_request_event(payload, db)
            log.info("processing_pr_event_success", 
                     message=f"Successfully processed PR #{payload.number}",
                     user=payload.pull_request.user.login,
                     diff_url=payload.pull_request.diff_url)

        except Exception as e:
            log.error("processing_pr_event_error", 
                      message=f"Error occurred while processing PR #{payload.number}",
                      error_type=type(e).__name__, 
                      error=str(e),
                      traceback=traceback.format_exc())
            # Log the error and return a 500 since this is an internal failure, not a validation failure
            raise HTTPException(status_code=500, detail=f"Internal server error: {type(e).__name__}")

    return {"status": "accepted", "message": "PR event received"}