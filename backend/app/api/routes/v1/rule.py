from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.rule_service import CustomRuleService
from typing import List
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.get("/", response_model=List[CustomRule])
async def list_rules(
    current_user: dict = Depends(get_current_user),
):
    """
    
    """