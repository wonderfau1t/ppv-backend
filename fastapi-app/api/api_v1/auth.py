from typing import Annotated

from fastapi import APIRouter, Depends, Response

from api.dependencies.services import get_auth_service, get_user_service
from core.schemas.auth import LoginSchema, RegisterSchema
from core.services.auth_service import AuthService
from core.services.user_service import UserService

router = APIRouter()


@router.post("/register", summary="Регистрация")
async def register(
    service: Annotated[UserService, Depends(get_user_service)],
    data: RegisterSchema,
):
    user_id = await service.register(data)
    return user_id


@router.post("/login", summary="Логин")
async def login(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    data: LoginSchema,
):
    role, token = await service.login(data)
    response.set_cookie("access_token", token, httponly=True, secure=True, samesite="none")
    return {"role": role}


@router.get("/check-auth", summary="Проверка аутентификации")
async def is_authenticated():
    return


@router.get("/logout", summary="Логаут (чистка куки)")
async def logout(
    response: Response,
):
    response.delete_cookie("access_token")
    return {"status": "success"}
