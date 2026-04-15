from fastapi import APIRouter
from app.api.routes import analytics, auth, health, webhooks

api_router = APIRouter()

api_router.include_router(analytics.router)
api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(webhooks.router)
