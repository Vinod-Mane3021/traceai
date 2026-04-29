from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_current_user, get_db
from app.services.rule_service import CustomRuleService
from app.schemas.rule import CustomRule, RuleCreate, RuleUpdate

router = APIRouter(prefix="/rules", tags=["Rules"])

@router.get("/repository/{repository_id}", response_model=List[CustomRule])
async def list_rules(
    repository_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all custom rules for a specific repository.
    """
    service = CustomRuleService(db)
    return await service.get_all_rules_for_repo(repository_id)

@router.post("/", response_model=CustomRule, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_in: RuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new custom rule.
    """
    service = CustomRuleService(db)
    return await service.add_custom_rule(
        repository_id=rule_in.repository_id,
        rule_text=rule_in.rule_text,
        is_active=rule_in.is_active
    )

@router.get("/{rule_id}", response_model=CustomRule)
async def get_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a specific custom rule by ID.
    """
    service = CustomRuleService(db)
    rule = await service.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.patch("/{rule_id}", response_model=CustomRule)
async def update_rule(
    rule_id: int,
    rule_in: RuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update an existing custom rule.
    """
    service = CustomRuleService(db)
    rule = await service.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Use existing values if not provided in request
    rule_text = rule_in.rule_text if rule_in.rule_text is not None else rule.rule_text
    is_active = rule_in.is_active if rule_in.is_active is not None else rule.is_active
    
    return await service.update_rule(rule_id, rule_text, is_active)

@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a custom rule.
    """
    service = CustomRuleService(db)
    rule = await service.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await service.delete_rule(rule_id)
    return None
