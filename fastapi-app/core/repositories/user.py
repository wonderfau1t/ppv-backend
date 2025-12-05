from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import UserAuth, UserData


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_data: UserData) -> int:
        self.session.add(user_data)
        await self.session.commit()
        return user_data.id

    async def list(self):
        stmt = select(UserAuth)
        users = await self.session.scalars(stmt)

        return users.all()

    async def get_by_login(self, login: str):
        stmt = select(UserAuth).where(UserAuth.login == login)
        user = await self.session.scalar(stmt)

        return user

    async def update(self):
        pass

    async def delete(self):
        pass
