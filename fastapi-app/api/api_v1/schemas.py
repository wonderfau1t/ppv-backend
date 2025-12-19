from typing import Annotated, Literal

from fastapi import APIRouter, Depends

from api.dependencies.services import get_schemas_service
from core.schemas.table_schemas import TableSchema
from core.services import SchemaService

router = APIRouter()


@router.get(
    "/{schema_name}", response_model=TableSchema, summary="Получить схему таблицы по ее имени"
)
async def get_schema_by_name(
    service: Annotated[SchemaService, Depends(get_schemas_service)],
    schema_name: Literal[
        "users", "admin-users", "matches-history", "user-matches-history", "match-with-sets", "top-players"
    ],
) -> TableSchema:
    schema = service.get(schema_name)
    return schema
