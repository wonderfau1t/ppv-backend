from typing import List

from core.exceptions.crud import NotFoundError
from core.repositories import RoleRepository
from core.schemas.resources import SelectBoxItem


class ResourcesService:
    def __init__(self, role_repo: RoleRepository) -> None:
        self.role_repo = role_repo

    async def get_roles_list(self) -> List[SelectBoxItem]:
        roles = await self.role_repo.get()
        if not roles:
            raise NotFoundError("Roles not found")

        return [SelectBoxItem(id=role.code, name=role.name) for role in roles]
