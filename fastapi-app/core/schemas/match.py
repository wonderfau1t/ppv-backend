from datetime import date, datetime
from typing import List
from .shared import AvatarSchema


from .base import BaseSchema


class MatchListItemPlayerSchema(BaseSchema):
    id: int
    full_name: str
    avatar: AvatarSchema


class MatchListItemSchema(BaseSchema):
    id: int
    date: date
    player1: MatchListItemPlayerSchema
    player2: MatchListItemPlayerSchema
    score: str
    winner: MatchListItemPlayerSchema
    type: str


class MatchesListResponse(BaseSchema):
    total: int
    limit: int
    offset: int
    items: List[MatchListItemSchema]


class MatchDetailsPlayerScheme(BaseSchema):
    id: int
    full_name: str
    avatar: AvatarSchema
    is_winner: bool
    score: int
    sets: List[int]


class MatchDetailsResponse(BaseSchema):
    type: str
    datetime: datetime
    duration_in_minutes: int
    player1: MatchDetailsPlayerScheme
    player2: MatchDetailsPlayerScheme


class TopPlayerItemSchema(BaseSchema):
    place: int
    player: MatchListItemPlayerSchema
    total_matches_duration: int
    total_games_count: int


class TopPlayersResponse(BaseSchema):
    items: List[TopPlayerItemSchema]


class LoadPeriodResponse(BaseSchema):
    labels: List[str]
    data: List[int]

class TopDaysAndPeriodResponse(BaseSchema):
    top_days: List[str]
    top_period: str
