from collections import defaultdict
from typing import List, Literal

from core.exceptions.crud import NotFoundError
from core.models import Match, MatchSet
from core.repositories import MatchRepository
from core.schemas.match import (
    LoadPeriodResponse,
    MatchDetailsPlayerScheme,
    MatchDetailsResponse,
    MatchesListResponse,
    MatchListItemPlayerSchema,
    MatchListItemSchema,
    TopDaysAndPeriodResponse,
    TopPlayerItemSchema,
    TopPlayersResponse,
)
from core.schemas.session import GetSessionResponse, GetStatsResponse, SetSchema
from core.schemas.shared import AvatarSchema, PlayerSchema
from core.schemas.user import (
    MyProfileMatchesListItemSchema,
    MyProfileMatchesListResponse,
    MyProfilePlayerSchema,
)
from core.utils.date import get_current_day, get_current_month, get_current_week, get_current_year

MONTHS_RU = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]

DAYS_RU = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
TIME_INTERVALS = [f"{h}:00-{h + 2}:00" for h in range(8, 20, 2)]


class MatchService:
    def __init__(self, repo: MatchRepository) -> None:
        self.repo = repo

    async def list(self, limit: int, offset: int) -> MatchesListResponse:
        total, matches_orm = await self.repo.list(limit=limit, offset=offset)
        matches_schema = {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [
                MatchListItemSchema(
                    id=match.id,
                    date=match.datetime.date(),
                    player1=MatchListItemPlayerSchema(
                        id=match.player1.id,
                        full_name=match.player1.full_name,
                        avatar=AvatarSchema(
                            alter=match.player1.initials, path=match.player1.avatar_url
                        ),
                    ),
                    player2=MatchListItemPlayerSchema(
                        id=match.player2.id,
                        full_name=match.player2.full_name,
                        avatar=AvatarSchema(
                            alter=match.player2.initials, path=match.player2.avatar_url
                        ),
                    ),
                    score=f"{match.player1_score}:{match.player2_score}",
                    winner=MatchListItemPlayerSchema(
                        id=match.winner.id,
                        full_name=match.winner.full_name,
                        avatar=AvatarSchema(
                            alter=match.winner.initials, path=match.winner.avatar_url
                        ),
                    ),
                    type=match.type,
                )
                for match in matches_orm
            ],
        }

        return MatchesListResponse.model_validate(matches_schema)

    async def get_by_id(self, id: int) -> MatchDetailsResponse:
        match = await self.repo.get_by_id(id)
        if not match:
            raise NotFoundError(f"Match {id} not found")

        match_schema = MatchDetailsResponse(
            type=match.type,
            datetime=match.datetime,
            duration_in_minutes=match.duration_in_minutes or 0,
            player1=MatchDetailsPlayerScheme(
                id=match.player1_id,
                full_name=match.player1.full_name,
                avatar=AvatarSchema(alter=match.player1.initials, path=match.player1.avatar_url),
                is_winner=(True if match.winner_id == match.player1_id else False),
                score=match.player1_score if match.player1_score is not None else 0,
                sets=[match_set.player1_score for match_set in match.sets],
            ),
            player2=MatchDetailsPlayerScheme(
                id=match.player2_id,
                full_name=match.player2.full_name,
                avatar=AvatarSchema(alter=match.player2.initials, path=match.player2.avatar_url),
                is_winner=(True if match.winner_id == match.player2_id else False),
                score=match.player2_score if match.player2_score is not None else 0,
                sets=[match_set.player2_score for match_set in match.sets],
            ),
        )

        return match_schema

    async def get_matches_by_user_id(
        self, id: int, limit: int, offset: int
    ) -> MyProfileMatchesListResponse:
        total, matches = await self.repo.get_by_user_id(id, limit, offset)
        if not matches:
            raise NotFoundError("0 matches")

        matches_dtos = []
        for match in matches:
            p1 = MyProfilePlayerSchema(
                id=match.player1_id,
                full_name=match.player1.full_name,
                avatar=AvatarSchema(alter=match.player1.initials, path=match.player1.avatar_url),
            )
            p2 = MyProfilePlayerSchema(
                id=match.player2_id,
                full_name=match.player2.full_name,
                avatar=AvatarSchema(alter=match.player2.initials, path=match.player2.avatar_url),
            )
            opponent = p1 if p1.id != id else p2

            winner = p1 if match.winner_id == p1.id else p2

            match_dto = MyProfileMatchesListItemSchema(
                id=match.id,
                date=match.datetime.date(),
                opponent=opponent,
                score=f"{match.player1_score}:{match.player2_score}",
                winner=winner,
                type=match.type,
            )
            matches_dtos.append(match_dto)

        return MyProfileMatchesListResponse(
            total=total,
            limit=limit,
            offset=offset,
            items=matches_dtos,
        )

    async def get_top_players(self) -> TopPlayersResponse:
        users = await self.repo.get_top_players()
        if not users:
            raise NotFoundError("Users not found")

        place = 1
        result: List[TopPlayerItemSchema] = []

        for user in users:
            result.append(
                TopPlayerItemSchema(
                    place=place,
                    player=MatchListItemPlayerSchema(
                        id=user.id,
                        full_name=user.full_name,
                        avatar=AvatarSchema(alter=user.initials, path=user.avatar_url),
                    ),
                    total_matches_duration=user.stats.total_matches_duration,
                    total_games_count=user.stats.amateur_games_count,
                )
            )
            place += 1

        return TopPlayersResponse(items=result)

    async def get_load_by_period(
        self, period: Literal["day", "week", "month", "year"]
    ) -> LoadPeriodResponse:
        match period:
            case "day":
                date_from, date_to = get_current_day()
            case "week":
                date_from, date_to = get_current_week()
            case "month":
                date_from, date_to = get_current_month()
            case "year":
                date_from, date_to = get_current_year()

        games = await self.repo.get_load_by_period(date_from, date_to)

        counts = defaultdict(int)

        if period == "year":
            labels = MONTHS_RU
            for game in games:
                counts[MONTHS_RU[game.datetime.month - 1]] += 1
        elif period == "month":
            labels = [f"Неделя {i}" for i in range(1, 6)]
            for game in games:
                week_num = ((game.datetime.day - 1) // 7) + 1
                counts[f"Неделя {week_num}"] += 1
        elif period == "week":
            labels = DAYS_RU
            for game in games:
                day_idx = game.datetime.weekday()
                counts[DAYS_RU[day_idx]] += 1
        elif period == "day":
            labels = TIME_INTERVALS
            for game in games:
                hour = game.datetime.hour
                if 8 <= hour < 20:
                    start_hour = 8 + 2 * ((hour - 8) // 2)
                    interval_label = f"{start_hour}:00-{start_hour + 2}:00"
                    counts[interval_label] += 1

        data = [counts.get(label, 0) for label in labels]

        return LoadPeriodResponse(labels=labels, data=data)

    async def calculate_extra_stats(self) -> TopDaysAndPeriodResponse:
        date_from, date_to = get_current_week()
        matches = await self.repo.get_load_by_period(date_from, date_to)

        day_counts = defaultdict(int)
        time_interval_counts = defaultdict(int)

        for match in matches:
            dt = match.datetime

            day_name = DAYS_RU[dt.weekday()]
            day_counts[day_name] += 1

            hour = dt.hour
            if 8 <= hour < 20:
                start_hour = 8 + 2 * ((hour - 8) // 2)
                interval = f"{start_hour}:00-{start_hour + 2}:00"
                time_interval_counts[interval] += 1

        top_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)[:2]

        top_days_result = [day for day, _ in top_days]

        top_period = None
        if time_interval_counts:
            interval, _ = max(time_interval_counts.items(), key=lambda x: x[1])
            top_period = interval

        return TopDaysAndPeriodResponse(
            top_days=top_days_result, top_period=top_period if top_period is not None else ""
        )

    async def get_session(self) -> GetSessionResponse:
        match = await self.repo.get_active_match()
        response = GetSessionResponse(
            is_live=bool(match),
            webRTC_url="http://147.45.159.99:8888/live/tennis/" if match else None,
        )
        return response

    async def get_session_stats(self) -> GetStatsResponse:
        match = await self.repo.get_active_match()
        if not match:
            raise

        last_set = await self.repo.get_last_set_of_match(match.id)
        if not last_set:
            raise

        return GetStatsResponse(
            player1=PlayerSchema(
                id=match.player1_id,
                full_name=match.player1.full_name,
                avatar=AvatarSchema(
                    alter=match.player1.initials,
                    path=match.player1.avatar_url,
                ),
            ),
            player2=PlayerSchema(
                id=match.player2_id,
                full_name=match.player2.full_name,
                avatar=AvatarSchema(
                    alter=match.player2.initials,
                    path=match.player2.avatar_url,
                ),
            ),
            score=f"{match.player1_score} – {match.player2_score}",
            set=SetSchema(
                label=f"Партия {last_set.set_number}",
                score=f"{last_set.player1_score} – {last_set.player2_score}",
            ),
        )

    async def create_session(self, creator_id: int, invited_id: int, best_of: int):
        match = Match(
            duration_in_minutes=0,
            player1_id=creator_id,
            player2_id=invited_id,
            player1_score=0,
            player2_score=0,
            sets=[MatchSet(
                set_number=i,
                player2_score=0,
                player1_score=0,
            ) for i in range(1, best_of + 1)]
        )
        id = await self.repo.create_session(match)
        return id

    async def start_session(self):
        await self.repo.start_session()