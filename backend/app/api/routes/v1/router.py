from fastapi import APIRouter
from app.api.routes.v1 import analytics, auth, webhooks

v1_router = APIRouter()

v1_router.include_router(analytics.router)
v1_router.include_router(auth.router)
v1_router.include_router(webhooks.router)
