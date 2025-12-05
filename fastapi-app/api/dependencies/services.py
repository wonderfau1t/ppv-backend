from typing import Annotated

from fastapi import Depends

from core.repositories import MatchRepository, UserRepository
from core.services import AuthService, MatchService, UserService

from .repositories import get_match_repository, get_user_repository


def get_user_service(repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return UserService(repo)


def get_auth_service(repo: Annotated[UserRepository, Depends(get_user_repository)]):
    return AuthService(repo)


def get_match_service(repo: Annotated[MatchRepository, Depends(get_match_repository)]):
    return MatchService(repo)
