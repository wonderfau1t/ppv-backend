from typing import List
from core.exceptions.basic import NotFoundError
from core.models import UserAuth, UserData
from core.repositories import UserRepository
from core.schemas.auth import RegisterSchema
from core.schemas.user import MyProfileMatchesListResponse, MyProfileResponse, MyProfileStatsResponse, UsersListResponse
from core.utils.bcrypt import hash_password


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def register(self, data: RegisterSchema):
        exists = await self.repo.get_by_login(data.login)
        if exists:
            raise ValueError("login already exists")

        user_auth = UserAuth(
            login=data.login, password_hash=hash_password(data.password)
        )
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
                full_name=" ".join([user.last_name, user.first_name, user.middle_name]),
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
            middle_name=user.middle_name,
            last_name=user.last_name,
            login=user.user_auth.login,
            role="Пользователь",
        )

        return dto
    
    async def get_stats(self, id: int) -> MyProfileStatsResponse:
        ...

    # async def get_matches_of_user(self, id: int) -> MyProfileMatchesListResponse:
    #     matches = await self.repo.get

