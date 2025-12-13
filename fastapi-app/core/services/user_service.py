import os
from typing import List
import uuid

from fastapi import UploadFile

from core import settings
from core.exceptions.auth import InvalidCredentialsError
from core.exceptions.basic import NotFoundError
from core.models import UserAuth, UserData
from core.repositories import UserRepository
from core.schemas.auth import RegisterSchema
from core.schemas.user import (
    AvatarSchema,
    ChangePasswordRequest,
    MyProfileResponse,
    MyProfileStatsResponse,
    UpdateProfileRequest,
    UsersListResponse,
)
from core.utils.bcrypt import check_password, hash_password


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def register(self, data: RegisterSchema):
        exists = await self.repo.get_by_login(data.login)
        if exists:
            raise ValueError("login already exists")

        user_auth = UserAuth(login=data.login, password_hash=hash_password(data.password))
        user_data = UserData(
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            user_auth=user_auth,
        )
        user_id = await self.repo.create(user_data)

        return user_id

    async def list(self) -> List[UsersListResponse]:
        users = await self.repo.list_of_user_data()
        if not users:
            raise NotFoundError("Table of users is empty")

        dtos = [
            UsersListResponse(
                id=user.id,
                full_name=user.full_name,
                avatar=AvatarSchema(alter=user.initials, path=user.avatar_url),
            )
            for user in users
        ]

        return dtos

    async def get_by_id(self, id: int) -> MyProfileResponse:
        user = await self.repo.get_by_id(id)
        if not user:
            raise NotFoundError(f"User {id} not found")

        dto = MyProfileResponse(
            id=user.id,
            first_name=user.first_name,
            middle_name=user.middle_name if user.middle_name is not None else "",
            last_name=user.last_name,
            avatar=AvatarSchema(alter=user.initials, path=user.avatar_url),
            login=user.user_auth.login,
            role="Пользователь",
        )

        return dto

    async def get_stats(self, id: int) -> MyProfileStatsResponse:
        stats = await self.repo.get_stats(id)
        if not stats:
            raise NotFoundError(f"Stats of User {id} not found")

        dto = MyProfileStatsResponse.model_validate(stats)

        return dto

    async def update_profile(self, id: int, data: UpdateProfileRequest):
        user = await self.repo.get_by_id_with_data(id)
        if not user:
            raise NotFoundError(f"User {id} not found")

        return await self.repo.update_profile(
            user=user,
            login=data.login,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
        )

    async def update_password(self, id, data: ChangePasswordRequest):
        user = await self.repo.get_auth_data_by_id(id)
        if not user:
            raise NotFoundError(f"User {id} not found")

        if not check_password(data.current_password, user.password_hash):
            raise InvalidCredentialsError("Invalid password")

        return await self.repo.update_password(user, hash_password(data.new_password))
    
    async def upload_avatar(self, id: int, file: UploadFile):
        if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
            raise
        if file.size and file.size > 5 * 1024 * 1024:
            raise

        filename = f"{uuid.uuid4()}.jpg"
        relative_path = f"avatars/{filename}"
        absolute_path = os.path.join(settings.media.root, relative_path)

        await self.repo.save_file(file, absolute_path)
        await self.repo.update_avatar_url(id, f"{settings.media.url}/{relative_path}")

    # async def get_matches_of_user(self, id: int) -> MyProfileMatchesListResponse:
    #     matches = await self.repo.get
