from .base import BaseSchema
from .shared import PlayerSchema


class GetSessionResponse(BaseSchema):
    is_live: bool
    webRTC_url: str | None


class SetSchema(BaseSchema):
    label: str
    score: str


class GetStatsResponse(BaseSchema):
    player1: PlayerSchema
    player2: PlayerSchema
    score: str
    set: SetSchema


class CreateSession(BaseSchema):
    player_id: int
    best_of: int
