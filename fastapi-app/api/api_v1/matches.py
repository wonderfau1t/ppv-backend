from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies.services import get_match_service
from core.exceptions.basic import NotFoundError
from core.schemas.match import MatchDetailsResponse, MatchesListResponse
from core.services.match_service import MatchService

router = APIRouter()


@router.get("", response_model=MatchesListResponse, summary="Список сыгранных матчей")
async def list(
    service: Annotated[MatchService, Depends(get_match_service)],
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
):
    try:
        matches = await service.list(limit=limit, offset=offset)
    except NotFoundError as e:
        raise HTTPException(404, detail={"error": str(e)})

    return matches


@router.get("/table-schema")
async def get_table_schema():
    response = {
        "columns": [
            {"key": "id", "title": "ID", "type": "number"},
            {"key": "date", "title": "Дата", "type": "date"},
            {
                "key": "player1",
                "title": "Игрок 1",
                "type": "player",
                "fields": [
                    {"key": "id", "type": "number"},
                    {"key": "fullName", "type": "str"},
                ],
            },
            {
                "key": "player2",
                "title": "Игрок 2",
                "type": "player",
                "fields": [
                    {"key": "id", "type": "number"},
                    {"key": "fullName", "type": "str"},
                ],
            },
            {"key": "score", "title": "Счет", "type": "str"},
            {
                "key": "winner",
                "title": "Победитель",
                "type": "player",
                "fields": [
                    {"key": "id", "type": "number"},
                    {"key": "fullName", "type": "str"},
                ],
            },
            {"key": "type", "title": "Тип игры", "type": "str"},
        ]
    }

    return response


@router.get(
    "/{id}",
    response_model=MatchDetailsResponse,
    summary="Информация по конкретному матчу",
)
async def get_by_id(service: Annotated[MatchService, Depends(get_match_service)], id: int):
    try:
        match = await service.get_by_id(id)
    except NotFoundError as e:
        raise HTTPException(404, detail={"error": str(e)})

    return match
