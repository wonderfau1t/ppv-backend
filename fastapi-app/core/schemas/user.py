from datetime import date
from typing import List

from core.schemas.base import BaseSchema
from core.schemas.match import AvatarSchema
from core.models.user import UserStatus


class UpdateProfileRequest(BaseSchema):
    first_name: str
    middle_name: str | None
    last_name: str
    login: str


class ChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str


# ---- Список пользователей в системе ----
class UsersListResponse(BaseSchema):
    id: int
    full_name: str
    avatar: AvatarSchema
    amateur_games_count: int
    wins_count: int


class RoleSchema(BaseSchema):
    id: int
    name: str


class StatusSchema(BaseSchema):
    id: str
    name: str


class AdminUsersListResponse(UsersListResponse):
    role: RoleSchema
    status: StatusSchema


# ---- Просмотр своего профиля ----
class MyProfileResponse(BaseSchema):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    avatar: AvatarSchema
    role: str
    login: str


# ---- Просмотр своей статистики ----
class MyProfileStatsResponse(BaseSchema):
    amateur_games_count: int
    tournament_games_count: int
    wins_count: int
    losses_count: int
    average_match_duration: int
    average_time_to_point: int
    total_matches_duration: int


# ---- Список матчей ----
class MyProfilePlayerSchema(BaseSchema):
    id: int
    full_name: str
    avatar: AvatarSchema


class MyProfileMatchesListItemSchema(BaseSchema):
    id: int
    date: date
    opponent: MyProfilePlayerSchema
    score: str
    winner: MyProfilePlayerSchema
    type: str


class MyProfileMatchesListResponse(BaseSchema):
    total: int
    limit: int
    offset: int
    items: List[MyProfileMatchesListItemSchema]
