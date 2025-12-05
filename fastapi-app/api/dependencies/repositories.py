from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from core.repositories import MatchRepository, UserRepository


def get_user_repository(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> UserRepository:
    return UserRepository(session)


def get_match_repository(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
) -> MatchRepository:
    return MatchRepository(session)
