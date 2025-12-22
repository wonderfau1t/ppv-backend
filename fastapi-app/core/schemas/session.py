from .base import BaseSchema


class GetSessionResponse(BaseSchema):
    is_live: bool
    webRTC_url: str | None


class SetSchema(BaseSchema):
    label: str
    score: str


class AvatarSchema(BaseSchema):
    alter: str
    path: str | None


class PlayerSchema(BaseSchema):
    id: str
    full_name: str
    avatar: AvatarSchema


class GetStatsResponse(BaseSchema):
    player1: PlayerSchema
    player2: PlayerSchema
    score: str
    set: SetSchema


class CreateSession(BaseSchema):
    player_id: int
