from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.services import get_match_service
from core.exceptions.basic import NotFoundError
from core.schemas.match import MatchDetailsResponse, MatchesListResponse
from core.services.match_service import MatchService

router = APIRouter()


@router.get("", response_model=MatchesListResponse, summary="Список сыгранных матчей")
async def list(service: Annotated[MatchService, Depends(get_match_service)]):
    try:
        matches = await service.list()
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
                "type": "object",
                "fields": [
                    {"key": "id", "type": "number"},
                    {"key": "fullName", "type": "str"},
                ],
            },
            {
                "key": "player2",
                "title": "Игрок 2",
                "type": "object",
                "fields": [
                    {"key": "id", "type": "number"},
                    {"key": "fullName", "type": "str"},
                ],
            },
            {"key": "score", "title": "Счет", "type": "str"},
            {
                "key": "winner",
                "title": "Победитель",
                "type": "object",
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
async def get_by_id(
    service: Annotated[MatchService, Depends(get_match_service)], id: int
):
    try:
        match = await service.get_by_id(id)
    except NotFoundError as e:
        raise HTTPException(404, detail={"error": str(e)})

    return match
