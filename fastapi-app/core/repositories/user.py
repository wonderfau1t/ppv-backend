import os
from typing import Sequence

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models import UserAuth, UserData, UserStats


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
        stmt = select(UserData).options(selectinload(UserData.stats))
        users = await self.session.scalars(stmt)

        return users.all()

    async def get_by_login(self, login: str) -> UserAuth | None:
        stmt = select(UserAuth).where(UserAuth.login == login).options(joinedload(UserAuth.role))
        user = await self.session.scalar(stmt)

        return user

    async def get_by_id(self, id: int) -> UserData | None:
        stmt = select(UserData).where(UserData.id == id).options(joinedload(UserData.user_auth))
        user = await self.session.scalar(stmt)

        return user

    async def update_stats(self, data: UserStats):
        self.session.add(data)
        await self.session.commit()

    async def get_stats(self, user_id: int) -> UserStats | None:
        stmt = select(UserStats).where(UserStats.id == user_id)
        stats = await self.session.scalar(stmt)

        return stats

    async def get_auth_data_by_id(self, id: int) -> UserAuth | None:
        stmt = select(UserAuth).where(UserAuth.id == id)
        user = await self.session.scalar(stmt)
        return user

    async def get_by_id_with_data(self, id: int):
        stmt = select(UserAuth).where(UserAuth.id == id).options(joinedload(UserAuth.user_data))
        user = await self.session.scalar(stmt)
        return user

    async def update_profile(
        self, user: UserAuth, login: str, first_name: str, middle_name: str | None, last_name: str
    ) -> UserAuth:
        user.login = login
        user.user_data.first_name = first_name
        user.user_data.middle_name = middle_name
        user.user_data.last_name = last_name

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def update_password(self, user: UserAuth, new_password: str):
        user.password_hash = new_password

        await self.session.commit()
        await self.session.refresh(user)

        return user

    async def save_file(self, file: UploadFile, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        async with aiofiles.open(path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)

    async def update_avatar_url(self, id: int, path: str | None):
        stmt = update(UserData).where(UserData.id == id).values(avatar_url=path)

        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self):
        pass

    async def get_list_with_data(self):
        stmt = select(UserAuth).options(
            joinedload(UserAuth.role), selectinload(UserAuth.user_data).selectinload(UserData.stats)
        )
        users = await self.session.scalars(stmt)

        return users.all()
