from fastapi import APIRouter

from .auth import router as auth_router
from .matches import router as matches_router
from .users import router as users_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router, prefix="/auth", tags=["Аутентификация"])
router.include_router(matches_router, prefix="/matches", tags=["Матчи"])
router.include_router(users_router, prefix="/users", tags=["Пользователи"])
