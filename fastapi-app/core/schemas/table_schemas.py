from typing import List, Literal

from core.schemas.auth import BaseSchema


class ColumnSchema(BaseSchema):
    key: str
    title: str
    type: Literal["str", "number", "date", "player", "role", "status"]


class TableSchema(BaseSchema):
    columns: List[ColumnSchema]
