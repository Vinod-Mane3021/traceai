from fastapi import APIRouter
from app.api.routes.v1 import analytics, auth, webhooks
from app.api.routes import health

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(webhooks.router, prefix="/v1")
api_router.include_router(auth.router, prefix="/v1")
api_router.include_router(analytics.router, prefix="/v1")
