from fastapi import FastAPI
import uvicorn
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

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)

