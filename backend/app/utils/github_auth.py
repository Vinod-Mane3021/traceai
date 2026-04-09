import time
import jwt
from app.core.config import settings

def generate_github_app_jwt() -> str:
    """
    Generates a short-lived JWT using the GitHub App's private key.
    """
    payload = {
        # Issued at time (60 seconds in the past to allow for clock drift)
        "iat": int(time.time()) - 60,
        # JWT expiration time (10 minutes maximum)
        "exp": int(time.time() + (10*60)),
        # GitHub App's identifier
        "iss": settings.GITHUB_APP_ID
    }

    # Ensure the private key is properly formatted
    private_key = settings.GITHUB_APP_PRIVATE_KEY_PATH.replace("\\n", "\n")

    algorithm = "RS256"

    encoded_jwt = jwt.encode(payload, private_key, algorithm)
    return encoded_jwt
