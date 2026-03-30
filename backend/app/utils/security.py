import hmac
import hashlib
from fastapi import Request, HTTPException
from app.core.config import settings

async def verify_github_signature(request: Request, signature_header: str):
    """Verifies the HMAC SHA256 signature sent by GitHub."""
    if not signature_header:
        raise HTTPException(status_code=400, detail="Missing signature")

    payload_body = await request.body()

    # Use hmac.new for correct signature generation
    hash_object = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    )

    expected_signature = "sha256=" + hash_object.hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Invalid signature")