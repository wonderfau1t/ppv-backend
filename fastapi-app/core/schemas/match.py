from datetime import datetime
from typing import List

from .base import BaseSchema


class MatchListItemPlayerSchema(BaseSchema):
    id: int
    full_name: str


class MatchListItemSchema(BaseSchema):
    id: int
    date: datetime
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
