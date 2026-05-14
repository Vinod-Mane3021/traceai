from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.models.core import Organization

class OrganizationRepo:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def upsert_organization(self, github_installation_id: int, name: str, org_type: str) -> Organization:
        """Finds the organization by GitHub Installation ID, or creates it if it's new."""
        result = await self.db.execute(select(Organization).where(Organization.github_installation_id == github_installation_id))

        org = result.scalars().first()
        if not org:
            org = Organization(
                name=name,
                type=org_type,
                github_installation_id=github_installation_id,
            )
            self.db.add(org)
            await self.db.commit()

        return org