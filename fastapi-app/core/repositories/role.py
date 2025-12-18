from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Role


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, role: Role) -> int:
        self.session.add(role)
        await self.session.commit()
        return role.id

    async def get(self):
        stmt = select(Role)
        roles = await self.session.scalars(stmt)

        return roles.all()

    async def get_by_code(self, role_code: str):
        stmt = select(Role).where(Role.code == role_code)
        role = await self.session.scalar(stmt)

        return role
