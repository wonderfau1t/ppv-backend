from pydantic import BaseModel

from core.schemas.base import BaseSchema


class RegisterSchema(BaseSchema):
    login: str
    password: str
    first_name: str
    middle_name: str
    last_name: str


class LoginSchema(BaseSchema):
    login: str
    password: str


class JWTClaims(BaseSchema):
    user_id: int
    role: str
