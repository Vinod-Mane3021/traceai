from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.core import CustomRule

class RuleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_rules_for_repo(self, repository_id: int) -> list[str]:
        """Fetches all active custom security rules for a specific repository."""
        stmt = (
            select(CustomRule.rule_text)
            .where(CustomRule.repository_id == repository_id)
            .where(CustomRule.is_active == True)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        