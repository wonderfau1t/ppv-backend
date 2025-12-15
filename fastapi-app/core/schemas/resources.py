from .base import BaseSchema


class SelectBoxItem(BaseSchema):
    id: str | int
    name: str
