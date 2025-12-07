from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.models import UserAuth, UserData


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_data: UserData) -> int:
        self.session.add(user_data)
        await self.session.commit()
        return user_data.id

    async def list_of_user_auth(self) -> Sequence[UserAuth]:
        stmt = select(UserAuth)
        users = await self.session.scalars(stmt)

        return users.all()

    async def list_of_user_data(self) -> Sequence[UserData]:
        stmt = select(UserData)
        users = await self.session.scalars(stmt)

        return users.all()

    async def get_by_login(self, login: str) -> UserAuth | None:
        stmt = select(UserAuth).where(UserAuth.login == login)
        user = await self.session.scalar(stmt)

        return user

    async def get_by_id(self, id: int) -> UserData | None:
        stmt = (
            select(UserData)
            .where(UserData.id == id)
            .options(joinedload(UserData.user_auth))
        )
        user = await self.session.scalar(stmt)

        return user

    async def update(self):
        pass

    async def delete(self):
        pass
