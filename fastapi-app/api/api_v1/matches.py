from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.services import get_match_service
from core.exceptions.basic import NotFoundError
from core.schemas.match import MatchDetailsResponse, MatchesListResponse
from core.services.match_service import MatchService

router = APIRouter()


@router.get("/", response_model=MatchesListResponse)
async def list(service: Annotated[MatchService, Depends(get_match_service)]):
    matches = await service.list()

    return matches


@router.get("/{id}", response_model=MatchDetailsResponse)
async def get_by_id(
    service: Annotated[MatchService, Depends(get_match_service)], id: int
):
    try:
        match = await service.get_by_id(id)
    except NotFoundError as e:
        raise HTTPException(404, detail={"error": str(e)})

    return match
