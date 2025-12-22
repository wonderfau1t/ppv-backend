import datetime
from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models import Match, MatchSet, UserData, UserStats
from core.models.match import MatchStatus


class MatchRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def create(self, match_data: Match) -> int:
        self.session.add(match_data)
        await self.session.commit()
        return match_data.id

    async def create_with_stats(self, match: Match):
        self.session.add(match)
        await self.session.flush()

        await self._recalculate_player_stats(match.player1_id)
        await self._recalculate_player_stats(match.player2_id)

        await self.session.commit()
        return match.id

    async def _recalculate_player_stats(self, user_id: int):
        # Получаем игрока и его матчи
        result = await self.session.execute(
            select(Match).where((Match.player1_id == user_id) | (Match.player2_id == user_id))
        )
        matches = result.scalars().all()

        if not matches:
            return

        amateur_games = len(matches)
        tournament_games = 0
        wins = sum(1 for m in matches if m.winner_id == user_id)
        losses = amateur_games - wins

        total_duration = sum(m.duration_in_minutes for m in matches if m.duration_in_minutes)
        avg_duration = total_duration // amateur_games if amateur_games else 0

        # Среднее время за очко (условное)
        result_sets = await self.session.execute(
            select(MatchSet).where(MatchSet.match_id.in_([m.id for m in matches]))
        )
        sets = result_sets.scalars().all()

        total_points = 0
        for s in sets:
            if s.winner_id is not None:
                total_points += s.player1_score + s.player2_score

        avg_time_per_point = (total_duration * 60) // total_points if total_points else 0

        # Обновление UserStats
        stats = UserStats(
            id=user_id,
            amateur_games_count=amateur_games,
            tournament_games_count=tournament_games,
            wins_count=wins,
            losses_count=losses,
            average_match_duration=avg_duration,
            average_time_to_point=avg_time_per_point,
            total_matches_duration=total_duration,
        )

        await self.session.merge(stats)
        await self.session.flush()

    async def list(self, limit: int, offset: int) -> tuple[int, Sequence[Match]]:
        total_result = await self.session.execute(select(func.count()).select_from(Match))
        total = total_result.scalar_one()

        # stmt = select(Match).options(
        #     joinedload(Match.player1),
        #     joinedload(Match.player2),
        #     joinedload(Match.winner),
        # )

        page = (
            select(Match)
            .options(
                joinedload(Match.player1),
                joinedload(Match.player2),
                joinedload(Match.winner),
            )
            .order_by(Match.datetime.desc())
            .offset(offset)
            .limit(limit)
        )

        matches = await self.session.scalars(page)

        return total, matches.all()

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

    async def get_by_user_id(self, id: int, limit: int, offset: int) -> tuple[int, Sequence[Match]]:
        total_result = await self.session.execute(
            select(func.count())
            .select_from(Match)
            .where(or_(Match.player1_id == id, Match.player2_id == id))
        )
        total = total_result.scalar_one()

        stmt = (
            select(Match)
            .where(or_(Match.player1_id == id, Match.player2_id == id))
            .options(selectinload(Match.player1), selectinload(Match.player2))
            .order_by(Match.datetime.desc())
            .offset(offset)
            .limit(limit)
        )
        matches = await self.session.scalars(stmt)

        return total, matches.all()

    async def get_top_players(self) -> Sequence[UserData]:
        stmt = (
            select(UserData)
            .join(UserData.stats)
            .options(joinedload(UserData.stats))
            .order_by(UserStats.amateur_games_count.desc())
            .limit(3)
        )
        users = await self.session.scalars(stmt)
        return users.all()

    async def get_load_by_period(
        self,
        date_from: datetime.datetime,
        date_to: datetime.datetime,
    ):
        stmt = select(Match).where(
            Match.datetime >= date_from,
            Match.datetime < date_to,
        )

        result = await self.session.scalars(stmt)
        return result.all()

    async def get_last_set_of_match(self, match_id: int):
        stmt = select(MatchSet).where(MatchSet.match_id == match_id).order_by(MatchSet.set_number)
        sets = await self.session.scalars(stmt)
        sets = sets.all()

        for _set in sets:
            if _set.winner_id is None:
                return _set

    async def get_active_match(self):
        stmt = (
            select(Match)
            .where(Match.status == MatchStatus.IN_PROGRESS)
            .options(
                joinedload(Match.player1),
                joinedload(Match.player2),
                selectinload(Match.sets),
            )
        )
        match = await self.session.scalar(stmt)
        return match

    async def create_session(self, match: Match):
        self.session.add(match)
        await self.session.commit()

        return match.id

    async def start_session(self):
        stmt = select(Match).where(Match.status == MatchStatus.REGISTERED)
        match = await self.session.scalar(stmt)
        if not match:
            raise
        match.status = MatchStatus.IN_PROGRESS
        await self.session.commit()
