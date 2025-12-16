from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response, UploadFile, status

from api.dependencies import get_match_service, get_user_service, require_role
from core.schemas.user import (
    ChangePasswordRequest,
    MyProfileMatchesListResponse,
    MyProfileResponse,
    MyProfileStatsResponse,
    UpdateProfileRequest,
    UpdateRoleRequest,
    UsersListResponse,
)
from core.services import MatchService, UserService

router = APIRouter()


@router.get(
    "",
    summary="Список зарегистрированных пользователей",
    response_model=UsersListResponse,
    tags=["Админ"],
)
async def list(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
) -> UsersListResponse:
    users = await service.list(request.state.user.role, limit, offset)
    return users


@router.get(
    "/me",
    summary="Просмотр собственного профиля",
    response_model=MyProfileResponse,
)
async def get_my_profile(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
) -> MyProfileResponse:
    user = await service.get_by_id(request.state.user.user_id)
    return user


@router.put(
    "/me",
    summary="Обновление информации в профиле",
)
async def update_my_profile(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
    data: UpdateProfileRequest,
) -> Response:
    await service.update_profile(request.state.user.user_id, data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/me/avatar",
    summary="Загрузка фото личного профиля",
)
async def upload_avatar(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
    file: UploadFile,
) -> Response:
    await service.upload_avatar(request.state.user.user_id, file)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/me/avatar",
    summary="Удаление фото профиля",
)
async def delete_avatar(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
) -> Response:
    await service.delete_avatar(request.state.user.user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/me/password",
    summary="Смена пароля",
)
async def change_password(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
    data: ChangePasswordRequest,
) -> Response:
    update = await service.update_password(request.state.user.user_id, data)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me/stats",
    summary="Просмотр своей статистики",
    response_model=MyProfileStatsResponse,
)
async def get_my_stats(
    service: Annotated[UserService, Depends(get_user_service)],
    request: Request,
) -> MyProfileStatsResponse:
    stats = await service.get_stats(request.state.user.user_id)
    return stats


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


@router.patch(
    "/{id}/role",
    summary="Обновление роли пользователя",
    tags=["Админ"],
)
async def update_user_role(
    service: Annotated[UserService, Depends(get_user_service)],
    id: int,
    data: UpdateRoleRequest,
    user=Depends(require_role("admin")),
) -> Response:
    await service.update_role(id, data.code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "{id}/block",
    summary="Заблокировать / отклонить пользователя",
    tags=["Админ"],
)
async def block_user(
    service: Annotated[UserService, Depends(get_user_service)],
    id: int,
    user=Depends(require_role("admin")),
):
    await service.block_user(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "{id}/unblock",
    summary="Разблокировать / подтвердить пользователя",
    tags=["Админ"],
)
async def unblock_user(
    service: Annotated[UserService, Depends(get_user_service)],
    id: int,
    user=Depends(require_role("admin")),
):
    await service.unblock_user(id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
