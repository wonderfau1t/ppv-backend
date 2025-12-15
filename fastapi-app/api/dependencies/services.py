from typing import Annotated

from fastapi import Depends

from core.repositories import MatchRepository, RoleRepository, UserRepository
from core.services import AuthService, MatchService, SchemaService, UserService, schema_service
from core.services.resources_service import ResourcesService

from .repositories import get_match_repository, get_role_repository, get_user_repository


def get_user_service(repo: Annotated[UserRepository, Depends(get_user_repository)]) -> UserService:
    return UserService(repo)


def get_auth_service(repo: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repo)


def get_match_service(
    repo: Annotated[MatchRepository, Depends(get_match_repository)],
) -> MatchService:
    return MatchService(repo)


def get_schemas_service() -> SchemaService:
    return schema_service


def get_resources_service(
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
) -> ResourcesService:
    return ResourcesService(role_repo)
