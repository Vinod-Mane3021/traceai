from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.models.core import OrganizationMember

class OrganizationMemberRepo:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def add_member_to_organization(self, user_id: int, organization_id: int, role: str = "MEMBER") -> OrganizationMember:
        """Adds a member to an organization with the specified role."""
        org_member = OrganizationMember(
            user_id=user_id,
            organization_id=organization_id,
            role=role
        )
        self.db.add(org_member)
        await self.db.commit()
        return org_member
    
    async def upsert_organization_member(self, user_id: int, organization_id: int, role: str = "MEMBER") -> OrganizationMember:
        """Upserts an organization member record."""
        result = await self.db.execute(
            select(OrganizationMember)
            .where(
                OrganizationMember.user_id == user_id,
                OrganizationMember.organization_id == organization_id
            )
        )
        org_member = result.scalars().first()
        if org_member:
            org_member.role = role  # Update role if member already exists
        else:
            org_member = OrganizationMember(
                user_id=user_id,
                organization_id=organization_id,
                role=role
            )
            self.db.add(org_member)
        
        await self.db.commit()
        return org_member