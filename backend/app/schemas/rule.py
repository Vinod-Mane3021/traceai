from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class RuleBase(BaseModel):
    rule_text: str
    is_active: bool = True

class RuleCreate(RuleBase):
    repository_id: int

class RuleUpdate(BaseModel):
    rule_text: Optional[str] = None
    is_active: Optional[bool] = None

class CustomRule(RuleBase):
    id: int
    repository_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
