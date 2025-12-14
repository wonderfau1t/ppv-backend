from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Role


class RoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, role: Role) -> int:
        self.session.add(role)
        await self.session.commit()
        return role.id
