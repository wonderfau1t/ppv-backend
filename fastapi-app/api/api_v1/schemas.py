from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.services import get_schemas_service
from core.schemas.table_schemas import TableSchema
from core.services import SchemaService

router = APIRouter()


@router.get("/{schema_name}", response_model=TableSchema)
async def get_schema_by_name(
    service: Annotated[SchemaService, Depends(get_schemas_service)],
    schema_name: Literal["users", "matches-history", "user-matches-history", "match-with-sets"],
) -> TableSchema:
    try:
        schema = service.get(schema_name)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    return schema
