import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.rule_repo import RuleRepository


logger = structlog.get_logger(__name__)


class CustomRuleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RuleRepository(db)

    def get_active_rules_for_repo(self, repository_id: int) -> list[str]:
        """Fetch all active custom security rules for a specific repository."""
        return self.repo.get_active_rules_for_repo(repository_id)
    
    def add_custom_rule(self, repository_id: int, rule_text: str, is_active: bool = True):
        """Adds a new custom security rule to the database."""
        return self.repo.add_custom_rule(repository_id, rule_text, is_active)

    def update_rule_status(self, rule_id: int, rule_text: str, is_active: bool):
        """Updates the status of an existing custom security rule."""
        return self.repo.update_rule_status(rule_id, rule_text, is_active)

    def delete_rule(self, rule_id: int):
        """Deletes an existing custom security rule."""
        return self.repo.delete_rule(rule_id)




