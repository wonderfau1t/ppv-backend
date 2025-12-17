from core.exceptions.crud import NotFoundError
from core.repositories import MatchRepository
from core.schemas.match import (
    AvatarSchema,
    MatchDetailsPlayerScheme,
    MatchDetailsResponse,
    MatchesListResponse,
    MatchListItemPlayerSchema,
    MatchListItemSchema,
    TopPlayerItemSchema,
    TopPlayersResponse,
)
from core.schemas.user import (
    MyProfileMatchesListItemSchema,
    MyProfileMatchesListResponse,
    MyProfilePlayerSchema,
)


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
                    date=match.date.date(),
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
            datetime=match.date,
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
                date=match.date.date(),
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

    # async def get_load(self, date_from: date, date_to: date):
    #     load = await self.repo.get_load(date_from, date_to)

    async def get_top_players(self) -> TopPlayersResponse:
        users = await self.repo.get_top_players()
        if not users:
            raise NotFoundError("Users not found")

        return TopPlayersResponse(
            players=[
                TopPlayerItemSchema(
                    id=user.id,
                    full_name=user.full_name,
                    avatar=AvatarSchema(alter=user.initials, path=user.avatar_url),
                    total_matches_duration=user.stats.total_matches_duration,
                    total_games_count=user.stats.amateur_games_count,
                )
                for user in users
            ]
        )
