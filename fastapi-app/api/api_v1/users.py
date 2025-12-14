from typing import Annotated, List

from fastapi import APIRouter, Depends, Query, Request, Response, UploadFile, status

from api.dependencies import get_match_service, get_user_service
from core.schemas.user import (
    AdminUsersListResponse,
    ChangePasswordRequest,
    MyProfileMatchesListResponse,
    MyProfileResponse,
    MyProfileStatsResponse,
    UpdateProfileRequest,
    UsersListResponse,
)
from core.services import MatchService, UserService

router = APIRouter()


# Список пользователей
@router.get(
    "",
    response_model=List[UsersListResponse] | List[AdminUsersListResponse],
    summary="Список зарегистрированных пользователей",
)
async def list(
    service: Annotated[UserService, Depends(get_user_service)], request: Request
) -> List[UsersListResponse] | List[AdminUsersListResponse]:
    print(request.state.user.role)
    users = await service.list(request.state.user.role)
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
    user = await service.get_by_id(request.state.user.user_id)
    return user


# Обновление информации в профиле
@router.put("/me")
async def update_my_profile(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
    data: UpdateProfileRequest,
):
    update = await service.update_profile(request.state.user.user_id, data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Установка фото профиля
@router.post("/me/avatar")
async def upload_avatar(
    service: Annotated[UserService, Depends(get_user_service)], request: Request, file: UploadFile
):
    await service.upload_avatar(request.state.user.user_id, file)


# Удаление фото профиля
@router.delete("/me/avatar")
async def delete_avatar(
    service: Annotated[UserService, Depends(get_user_service)], request: Request
):
    await service.delete_avatar(request.state.user.user_id)


# Смена пароля
@router.patch("/me/password")
async def change_password(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
    data: ChangePasswordRequest,
):
    update = await service.update_password(request.state.user.user_id, data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Просмотр статистики
@router.get(
    "/me/stats",
    summary="Просмотр своей статистики",
    response_model=MyProfileStatsResponse,
)
async def get_my_stats(
    service: Annotated[UserService, Depends(get_user_service)], request: Request
) -> MyProfileStatsResponse:
    stats = await service.get_stats(request.state.user.user_id)
    return stats


# Просмотреть список собственных матчей
@router.get(
    "/me/matches",
    summary="Просмотр списка матчей, в которых участвовал",
    response_model=MyProfileMatchesListResponse,
)
async def get_my_matches(
    service: Annotated[MatchService, Depends(get_match_service)],
    request: Request,
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
) -> MyProfileMatchesListResponse:
    matches = await service.get_matches_by_user_id(request.state.user.user_id, limit, offset)
    return matches


# Просмотреть профиль пользователя
@router.get("/{id}", summary="Просмотр профиля пользователя")
async def get_by_id(id: int):
    pass


# Просмотреть список матчей пользователя
@router.get("/{id}/matches", summary="Просмотр списка матчей выбранного пользователя")
async def get_user_matches(id: int):
    pass
