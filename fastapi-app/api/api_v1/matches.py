from typing import Annotated

from fastapi import APIRouter, Depends, Query

from api.dependencies.services import get_match_service
from core.schemas.match import MatchDetailsResponse, MatchesListResponse
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
    "/{id}",
    response_model=MatchDetailsResponse,
    summary="Информация по конкретному матчу",
)
async def get_by_id(service: Annotated[MatchService, Depends(get_match_service)], id: int):
    match = await service.get_by_id(id)
    return match
