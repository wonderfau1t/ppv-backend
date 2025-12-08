from typing import Annotated, List

from fastapi import APIRouter, Depends, Request

from api.dependencies import get_match_service, get_user_service
from core.schemas.user import (
    MyProfileMatchesListResponse,
    MyProfileResponse,
    MyProfileStatsResponse,
    UsersListResponse,
)
from core.services import MatchService, UserService

router = APIRouter()


# Список пользователей
@router.get(
    "",
    response_model=List[UsersListResponse],
    summary="Список зарегистрированных пользователей",
)
async def list(
    service: Annotated[UserService, Depends(get_user_service)],
) -> List[UsersListResponse]:
    try:
        users = await service.list()
    except:
        pass

    return users


# Просмотр собственного профиля
@router.get(
    "/me",
    response_model=MyProfileResponse,
    summary="Просмотр собственного профиля",
)
async def get_my_profile(
    service: Annotated[UserService, Depends(get_user_service)], request: Request
) -> MyProfileResponse:
    try:
        user = await service.get_by_id(request.state.user.user_id)
    except:
        pass

    return user


# Просмотр статистики
@router.get(
    "/me/stats",
    summary="Просмотр своей статистики",
    response_model=MyProfileStatsResponse,
)
async def get_my_stats(
    service: Annotated[UserService, Depends(get_user_service)], request: Request
) -> MyProfileStatsResponse:
    try:
        stats = await service.get_stats(request.user.user_id)
    except:
        pass

    return stats


# Просмотреть список собственных матчей
@router.get("/me/matches", summary="Просмотр списка матчей, в которых участвовал", response_model=MyProfileMatchesListResponse)
async def get_my_matches(service: Annotated[MatchService, Depends(get_match_service)], request: Request) -> MyProfileMatchesListResponse:
    try:
        matches = await service.get_matches_by_user_id(request.state.user.user_id)
    except:
        pass 
    return matches


# Просмотреть профиль пользователя
@router.get("/{id}", summary="Просмотр профиля пользователя")
async def get_by_id(id: int):
    pass


# Просмотреть список матчей пользователя
@router.get("/{id}/matches", summary="Просмотр списка матчей выбранного пользователя")
async def get_user_matches(id: int):
    pass
