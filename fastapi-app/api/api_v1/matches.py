from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from api.dependencies.services import get_match_service
from core.schemas.match import (
    LoadPeriodResponse,
    MatchDetailsResponse,
    MatchesListResponse,
    TopPlayersResponse,
)
from core.services.match_service import MatchService

router = APIRouter()


@router.get("", response_model=MatchesListResponse, summary="Список сыгранных матчей")
async def list(
    service: Annotated[MatchService, Depends(get_match_service)],
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
):
    matches = await service.list(limit=limit, offset=offset)
    return matches


@router.get(
    "/top-players",
    summary="Получение ТОП-3 игроков по количеству матчей",
    response_model=TopPlayersResponse,
)
async def get_top_player(
    service: Annotated[MatchService, Depends(get_match_service)],
) -> TopPlayersResponse:
    top = await service.get_top_players()
    return top


@router.get(
    "/{id}",
    summary="Информация по конкретному матчу",
    response_model=MatchDetailsResponse,
)
async def get_by_id(
    service: Annotated[MatchService, Depends(get_match_service)], id: int
) -> MatchDetailsResponse:
    match = await service.get_by_id(id)
    return match


@router.get("/load/{period}")
async def get_load_by_period(
    service: Annotated[MatchService, Depends(get_match_service)],
    period: Literal["day", "week", "month", "year"],
) -> LoadPeriodResponse:
    load = await service.get_load_by_period(period)
    return load
