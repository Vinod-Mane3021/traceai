import hmac
import hashlib
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Request, HTTPException
from app.core.config import settings

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Generates a local JWT for the user."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60 * 24 * 7) # 1 week default
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

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
