import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rule_repo import RuleRepository
from app.models.core import CustomRule


logger = structlog.get_logger(__name__)


class CustomRuleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RuleRepository(db)

    async def get_active_rules_for_repo(self, repository_id: int) -> list[str]:
        """Fetch all active custom security rules for a specific repository."""
        return await self.repo.get_active_rules_for_repo(repository_id)
    
    async def get_all_rules_for_repo(self, repository_id: int) -> list[CustomRule]:
        """Fetch all custom security rules for a specific repository."""
        return await self.repo.get_all_rules_for_repo(repository_id)

    async def get_rule_by_id(self, rule_id: int) -> CustomRule | None:
        """Fetch a specific custom security rule by ID."""
        return await self.repo.get_rule_by_id(rule_id)
    
    async def add_custom_rule(self, repository_id: int, rule_text: str, is_active: bool = True):
        """Adds a new custom security rule to the database."""
        return await self.repo.add_custom_rule(repository_id, rule_text, is_active)

    async def update_rule(self, rule_id: int, rule_text: str, is_active: bool):
        """Updates an existing custom security rule."""
        return await self.repo.update_rule_status(rule_id, rule_text, is_active)

    async def delete_rule(self, rule_id: int):
        """Deletes an existing custom security rule."""
        return await self.repo.delete_rule(rule_id)
