import os
import uuid

from fastapi import UploadFile

from core import settings
from core.exceptions.auth import InvalidCredentialsError
from core.exceptions.crud import AlreadyExistsError, NotFoundError
from core.models import UserAuth, UserData, UserStatus
from core.repositories import RoleRepository, UserRepository
from core.schemas.auth import RegisterSchema
from core.schemas.user import (
    AdminUsersListItem,
    AvatarSchema,
    ChangePasswordRequest,
    MyProfileResponse,
    MyProfileStatsResponse,
    PlayerSchema,
    RoleSchema,
    StatusSchema,
    UpdateProfileRequest,
    UsersListItem,
    UsersListResponse,
)
from core.utils.bcrypt import check_password, hash_password


class UserService:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository) -> None:
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def register(self, data: RegisterSchema) -> int:
        exists = await self.user_repo.get_by_login(data.login)
        if exists:
            raise AlreadyExistsError(f"login {data.login} already exists")

        user_auth = UserAuth(login=data.login, password_hash=hash_password(data.password))
        user_data = UserData(
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            user_auth=user_auth,
        )
        user_id = await self.user_repo.create(user_data)

        return user_id

    async def list(self, actor_role: str, limit: int, offset: int) -> UsersListResponse:
        total, users = await self.user_repo.get_list_with_data(limit, offset)

        if actor_role == "admin":
            return UsersListResponse(
                total=total,
                limit=limit,
                offset=offset,
                items=[
                    AdminUsersListItem(
                        id=user.id,
                        player=PlayerSchema(
                            id=user.id,
                            full_name=user.user_data.full_name,
                            avatar=AvatarSchema(
                                alter=user.user_data.initials,
                                path=user.user_data.avatar_url,
                            ),
                        ),
                        games_count=user.user_data.stats.amateur_games_count
                        + user.user_data.stats.tournament_games_count,
                        wins_count=user.user_data.stats.wins_count,
                        role=RoleSchema(
                            id=user.role.code,
                            name=user.role.name,
                        ),
                        status=StatusSchema(id=user.status.value, name=user.status.label),
                    )
                    for user in users
                ],
            )
        return UsersListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=[
                UsersListItem(
                    id=user.id,
                    player=PlayerSchema(
                        id=user.id,
                        full_name=user.user_data.full_name,
                        avatar=AvatarSchema(
                            alter=user.user_data.initials,
                            path=user.user_data.avatar_url,
                        ),
                    ),
                    games_count=user.user_data.stats.amateur_games_count
                    + user.user_data.stats.tournament_games_count,
                    wins_count=user.user_data.stats.wins_count,
                )
                for user in users
            ],
        )

    async def get_by_id(self, id: int) -> MyProfileResponse:
        user = await self.user_repo.get_by_id(id)
        if not user:
            raise NotFoundError(f"User {id} not found")

        return MyProfileResponse(
            id=user.id,
            first_name=user.first_name,
            middle_name=user.middle_name if user.middle_name is not None else "",
            last_name=user.last_name,
            avatar=AvatarSchema(alter=user.initials, path=user.avatar_url),
            login=user.user_auth.login,
            role="Пользователь",
        )

    async def get_stats(self, id: int) -> MyProfileStatsResponse:
        stats = await self.user_repo.get_stats(id)
        if not stats:
            raise NotFoundError(f"Stats of User {id} not found")

        return MyProfileStatsResponse.model_validate(stats)

    async def update_profile(self, id: int, data: UpdateProfileRequest):
        user = await self.user_repo.get_by_id_with_data(id)
        if not user:
            raise NotFoundError(f"User {id} not found")

        return await self.user_repo.update_profile(
            user=user,
            login=data.login,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
        )

    async def update_password(self, id, data: ChangePasswordRequest):
        user = await self.user_repo.get_auth_data_by_id(id)
        if not user:
            raise NotFoundError(f"User {id} not found")

        if not check_password(data.current_password, user.password_hash):
            raise InvalidCredentialsError("Invalid password")

        return await self.user_repo.update_password(user, hash_password(data.new_password))

    async def upload_avatar(self, id: int, file: UploadFile):
        if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
            raise
        if file.size and file.size > 5 * 1024 * 1024:
            raise

        user = await self.user_repo.get_by_id_with_data(id)
        old_avatar_path = None
        if user and user.user_data.avatar_url:
            old_avatar_path = os.path.join(
                settings.media.root, user.user_data.avatar_url.lstrip(settings.media.url + "/")
            )

        filename = f"{uuid.uuid4()}.jpg"
        relative_path = f"avatars/{filename}"
        absolute_path = os.path.join(settings.media.root, relative_path)

        await self.user_repo.save_file(file, absolute_path)
        await self.user_repo.update_avatar_url(id, f"{settings.media.url}/{relative_path}")

        if old_avatar_path and os.path.exists(old_avatar_path):
            try:
                os.remove(old_avatar_path)
            except Exception as e:
                print(f"Failed to remove old avatar: {e}")

    async def delete_avatar(self, id: int):
        user = await self.user_repo.get_by_id_with_data(id)
        avatar_path = None
        if user and user.user_data.avatar_url:
            print(user.user_data.avatar_url)
            avatar_path = os.path.join(
                settings.media.root,
                user.user_data.avatar_url.removeprefix(settings.media.url + "/"),
            )
        if avatar_path and os.path.exists(avatar_path):
            try:
                os.remove(avatar_path)
            except Exception as e:
                print(f"Failed to remove old avatar: {e}")

        await self.user_repo.update_avatar_url(id, None)

    async def update_role(self, user_id: int, role_code: str):
        user = await self.user_repo.get_user_auth_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        role = await self.role_repo.get_by_code(role_code)
        if not role:
            raise NotFoundError(f"Role {role_code} not found")

        await self.user_repo.update_role(user, role.id)

    async def block_user(self, user_id: int):
        user = await self.user_repo.get_user_auth_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        await self.user_repo.update_status(user, UserStatus.BLOCKED)

    async def unblock_user(self, user_id: int):
        user = await self.user_repo.get_user_auth_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")

        await self.user_repo.update_status(user, UserStatus.ACTIVE)
