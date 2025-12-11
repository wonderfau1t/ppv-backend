from datetime import date, datetime
from typing import List

from .base import BaseSchema


class AvatarSchema(BaseSchema):
    alter: str
    path: str


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


# class CreateMatchRequest(BaseSchema):
#     player1_id: int
#     player2_id: int
#     best_of: int


class MatchDetailsPlayerScheme(BaseSchema):
    id: int
    full_name: str
    is_winner: bool
    score: int
    sets: List[int]


class MatchDetailsResponse(BaseSchema):
    type: str
    datetime: datetime
    duration_in_minutes: int
    player1: MatchDetailsPlayerScheme
    player2: MatchDetailsPlayerScheme
