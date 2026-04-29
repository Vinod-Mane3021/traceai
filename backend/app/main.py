import uuid
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import structlog

from app.core.config import settings
from app.api.routes.router import api_router
from app.core.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = structlog.get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8081",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8081",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Include the aggregated API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"name": settings.APP_NAME, "description": settings.APP_DESCRIPTION, "version": settings.APP_VERSION}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
