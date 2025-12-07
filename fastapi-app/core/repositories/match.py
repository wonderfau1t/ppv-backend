from typing import Sequence

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models import Match


class MatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, match_data: Match) -> int:
        self.session.add(match_data)
        await self.session.commit()
        return match_data.id

    async def list(self) -> Sequence[Match]:
        stmt = select(Match).options(
            joinedload(Match.player1),
            joinedload(Match.player2),
            joinedload(Match.winner),
        )
        matches = await self.session.scalars(stmt)

        return matches.all()

    async def get_by_id(self, id: int) -> Match | None:
        stmt = (
            select(Match)
            .where(Match.id == id)
            .options(
                joinedload(Match.player1),
                joinedload(Match.player2),
                selectinload(Match.sets),
            )
        )
        match = await self.session.scalar(stmt)

        return match

    async def get_by_user_id(self, id: int) -> Sequence[Match]:
        stmt = (
            select(Match)
            .where(or_(Match.player1_id == id, Match.player2_id == id))
            .options(selectinload(Match.player1), selectinload(Match.player2))
        )
        matches = await self.session.scalars(stmt)

        return matches.all()
