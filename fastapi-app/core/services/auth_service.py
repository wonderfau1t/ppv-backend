from core.exceptions.auth import InvalidCredentialsError
from core.repositories import UserRepository
from core.schemas.auth import JWTClaims, LoginSchema
from core.utils.bcrypt import check_password
from core.utils.jwt import create_access_token


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    async def login(self, data: LoginSchema) -> tuple[str, str]:
        user = await self.repo.get_by_login(data.login)
        if not user:
            raise InvalidCredentialsError()

        valid = check_password(data.password, user.password_hash)
        if not valid:
            raise InvalidCredentialsError()

        token = create_access_token(JWTClaims(user_id=user.id, role="user"))

        return user.role.code, token

    # Если вдруг будем делать рефреш/сессионную
    async def logout(self):
        pass
