from core.models import UserAuth, UserData
from core.repositories import UserRepository
from core.schemas.auth import RegisterSchema
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

    async def list(self):
        pass
