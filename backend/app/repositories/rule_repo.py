from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
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
        rules = list(result.scalars().all())
        
        # End the transaction to avoid holding a connection idle during AI analysis.
        # We use commit() instead of rollback() because rollback() always expires all objects 
        # in the session, which would cause MissingGreenlet errors when accessing them 
        # (like db_pr.id) after the AI analysis gap.
        await self.session.commit()
        
        return rules

    async def get_all_rules_for_repo(self, repository_id: int) -> list[CustomRule]:
        """Fetches all custom security rules for a specific repository."""
        stmt = (
            select(CustomRule)
            .where(CustomRule.repository_id == repository_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_rule_by_id(self, rule_id: int) -> CustomRule | None:
        """Fetches a specific custom security rule by ID."""
        stmt = select(CustomRule).where(CustomRule.id == rule_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def add_custom_rule(self, repository_id: int, rule_text: str, is_active: bool = True) -> CustomRule:
        """Adds a new custom security rule to the database."""
        stmt = (
            insert(CustomRule)
            .values(repository_id=repository_id, rule_text=rule_text, is_active=is_active)
            .returning(CustomRule)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
    

    async def update_rule_status(self, rule_id: int, rule_text: str, is_active: bool) -> CustomRule:
        """Updates the status of an existing custom security rule."""
        stmt = (
            update(CustomRule)
            .where(CustomRule.id == rule_id)
            .values(rule_text=rule_text, is_active=is_active)
            .returning(CustomRule)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()
    
    async def delete_rule(self, rule_id: int) -> None:
        """Deletes an existing custom security rule."""
        stmt = (
            delete(CustomRule)
            .where(CustomRule.id == rule_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return None