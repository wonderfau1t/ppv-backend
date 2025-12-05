from pydantic import BaseModel


class RegisterSchema(BaseModel):
    login: str
    password: str
    first_name: str
    middle_name: str
    last_name: str


class LoginSchema(BaseModel):
    login: str
    password: str


class JWTClaims(BaseModel):
    user_id: int
    role: str
