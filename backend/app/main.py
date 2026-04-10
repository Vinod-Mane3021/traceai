import uuid
import time
from fastapi import FastAPI, Request
import uvicorn
import structlog

from app.core.config import settings
from app.api.routes.webhooks import router as webhooks_router
from app.core.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = structlog.get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)
    
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=f"{process_time:.4f}s"
    )
    
    return response

app.include_router(webhooks_router, prefix="/api/webhooks", tags=["Webhooks"])

@app.get("/")
async def read_root():
    return {"name": settings.APP_NAME, "description": settings.APP_DESCRIPTION, "version": settings.APP_VERSION}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)

