from typing import Annotated, List

from fastapi import APIRouter, Depends

from api.dependencies.services import get_resources_service
from core.schemas.resources import SelectBoxItem
from core.services import ResourcesService

router = APIRouter()


@router.get(
    "/role-select",
    response_model=List[SelectBoxItem],
    summary="Получение списка ролей для selectBox",
)
async def get_role_select(
    service: Annotated[ResourcesService, Depends(get_resources_service)],
) -> List[SelectBoxItem]:
    roles = await service.get_roles_list()
    return roles
