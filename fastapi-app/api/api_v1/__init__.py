from fastapi import APIRouter

from .auth import router as auth_router
from .matches import router as matches_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router, prefix="/auth")
router.include_router(matches_router, prefix="/matches")
