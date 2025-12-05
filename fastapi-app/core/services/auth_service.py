from core.exceptions.auth import InvalidCredentialsError
from core.exceptions.basic import NotFoundError
from core.repositories import UserRepository
from core.schemas.auth import JWTClaims, LoginSchema
from core.utils.bcrypt import check_password
from core.utils.jwt import create_access_token


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def login(self, data: LoginSchema) -> str:
        user = await self.repo.get_by_login(data.login)
        if not user:
            raise NotFoundError(f"User {data.login} does not exist")

        valid = check_password(data.password, user.password_hash)
        if not valid:
            raise InvalidCredentialsError("invalid password")

        token = create_access_token(JWTClaims(user_id=user.id, role="user"))

        return token

    # Если вдруг будем делать рефреш/сессионную
    async def logout(self):
        pass
