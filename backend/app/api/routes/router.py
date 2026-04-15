from fastapi import APIRouter
from app.api.routes.v1.router import v1_router
from app.api.routes import health

api_router = APIRouter()

# Include versioned routers
api_router.include_router(v1_router, prefix="/v1")

# Non-versioned or generic routes (e.g., health checks)
api_router.include_router(health.router)
