from app.models.core import Repository, PullRequest, Vulnerability, CustomRule
from sqlalchemy.orm import configure_mappers
import sys

try:
    configure_mappers()
    print("Mappers configured successfully!")
except Exception as e:
    print(f"Error configuring mappers: {e}")
    sys.exit(1)
