from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

@app.get("/")
async def read_root():
    return {"name": settings.APP_NAME, "description": settings.APP_DESCRIPTION, "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME} 