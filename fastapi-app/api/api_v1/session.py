from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_match_service
from core.schemas.session import CreateSession, GetSessionResponse, GetStatsResponse
from core.services import MatchService

router = APIRouter()


@router.get(
    "/live",
    summary="Получить активную сессию",
    response_model=GetSessionResponse,
)
async def get_sesion(
    service: Annotated[MatchService, Depends(get_match_service)],
) -> GetSessionResponse:
    session = await service.get_session()
    return session


@router.get(
    "/stats",
    summary="Получить статистику по аткивной сессии",
    response_model=GetStatsResponse,
    deprecated=True,
)
async def get_stats(
    service: Annotated[MatchService, Depends(get_match_service)],
) -> GetStatsResponse:
    stats = await service.get_session_stats()
    ...


@router.post(
    "/create",
    summary="Создать сессию",
    deprecated=True,
)
async def create_session(
    service: Annotated[MatchService, Depends(get_match_service)],
    data: CreateSession,
):
    await service.create_session()
    ...


@router.post(
    "/start",
    summary="Запустить игру (анализ)",
    deprecated=True,
)
async def start_session(
    service: Annotated[MatchService, Depends(get_match_service)],
): ...


@router.post(
    "/complete",
    summary="Досрочно завершить сессию",
    deprecated=True,
)
async def complete_session(
    service: Annotated[MatchService, Depends(get_match_service)],
): ...
