from datetime import date
from typing import List

from .base import BaseSchema
from .shared import AvatarSchema, PlayerSchema


class UpdateProfileRequest(BaseSchema):
    first_name: str
    middle_name: str | None
    last_name: str
    login: str


class ChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str


# ---- Список пользователей в системе ----
class UsersListItem(BaseSchema):
    id: int
    player: PlayerSchema
    games_count: int
    wins_count: int


class RoleSchema(BaseSchema):
    id: str
    name: str


class StatusSchema(BaseSchema):
    id: str
    name: str


class AdminUsersListItem(UsersListItem):
    role: RoleSchema
    status: StatusSchema


class UsersListResponse(BaseSchema):
    total: int
    limit: int
    offset: int
    items: List[UsersListItem] | List[AdminUsersListItem]


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


class MyProfileMatchesListItemSchema(BaseSchema):
    id: int
    date: date
    opponent: PlayerSchema
    score: str
    winner: PlayerSchema
    type: str


class MyProfileMatchesListResponse(BaseSchema):
    total: int
    limit: int
    offset: int
    items: List[MyProfileMatchesListItemSchema]


class UserProfile(BaseSchema):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    avatar: AvatarSchema
    role: str
    login: str


class UpdateRoleRequest(BaseSchema):
    code: str


class PendingUsersResponse(BaseSchema):
    total: int
    players: List[PlayerSchema]


class UserProfileResponse(BaseSchema):
    id: int
    full_name: str
    role: str
    avatar: AvatarSchema
    stats: MyProfileStatsResponse
