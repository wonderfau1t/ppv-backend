from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from api.dependencies.services import get_auth_service, get_user_service
from core.exceptions.auth import InvalidCredentialsError, UserNotFoundError
from core.schemas.auth import LoginSchema, RegisterSchema
from core.services.auth_service import AuthService
from core.services.user_service import UserService

router = APIRouter()


@router.post("/register", summary="Регистрация")
async def register(
    service: Annotated[UserService, Depends(get_user_service)],
    data: RegisterSchema,
):
    try:
        user_id = await service.register(data)
    except ValueError:
        raise HTTPException(status_code=409, detail={"error": "login already taken"})
    return user_id


@router.post("/login", summary="Логин")
async def login(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    data: LoginSchema,
):
    try:
        token = await service.login(data)
        response.set_cookie(
            "access_token", token, httponly=False, secure=True, samesite="none"
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=403, detail={"error": str(e)})
    return {"role": "user"}
