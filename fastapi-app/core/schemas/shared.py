from .base import BaseSchema

class AvatarSchema(BaseSchema):
    alter: str
    path: str | None

class PlayerSchema(BaseSchema):
    id: int
    full_name: str
    avatar: AvatarSchema