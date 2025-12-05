from pydantic import BaseModel


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "alias_generator": to_camel,
    }
