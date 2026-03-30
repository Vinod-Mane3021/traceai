import os
from app.core.config import settings
print(f"POSTGRES_HOST: '{settings.POSTGRES_HOST}'")
print(f"DATABASE_URL: '{settings.DATABASE_URL}'")
print("--- OS ENV ---")
for k, v in os.environ.items():
    if k.startswith("POSTGRES_"):
        print(f"{k}: '{v}'")
