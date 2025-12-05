from core.exceptions.basic import NotFoundError
from core.repositories import MatchRepository
from core.schemas.match import (
    MatchDetailsPlayerScheme,
    MatchDetailsResponse,
    MatchesListResponse,
    MatchListItemPlayerSchema,
    MatchListItemSchema,
)


class MatchService:
    def __init__(self, repo: MatchRepository) -> None:
        self.repo = repo

    async def list(self) -> MatchesListResponse:
        matches_orm = await self.repo.list()
        matches_schema = {
            "total": len(matches_orm),
            "matches": [
                MatchListItemSchema(
                    id=match.id,
                    date=match.date,
                    player1=MatchListItemPlayerSchema(
                        id=match.player1.id,
                        full_name=" ".join(
                            [
                                match.player1.last_name,
                                match.player1.first_name,
                                match.player1.middle_name,
                            ]
                        ),
                    ),
                    player2=MatchListItemPlayerSchema(
                        id=match.player2.id,
                        full_name=" ".join(
                            [
                                match.player2.last_name,
                                match.player2.first_name,
                                match.player2.middle_name,
                            ]
                        ),
                    ),
                    score=f"{match.player1_score}:{match.player2_score}",
                    winner=MatchListItemPlayerSchema(
                        id=match.winner.id,
                        full_name=" ".join(
                            [
                                match.winner.last_name,
                                match.winner.first_name,
                                match.winner.middle_name,
                            ]
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
                full_name=" ".join(
                    [
                        match.player1.last_name,
                        match.player1.first_name,
                        match.player1.middle_name,
                    ]
                ),
                is_winner=(True if match.winner_id == match.player1_id else False),
                score=match.player1_score if match.player1_score is not None else 0,
                sets=[match_set.player1_score for match_set in match.sets],
            ),
            player2=MatchDetailsPlayerScheme(
                id=match.player2_id,
                full_name=" ".join(
                    [
                        match.player2.last_name,
                        match.player2.first_name,
                        match.player2.middle_name,
                    ]
                ),
                is_winner=(True if match.winner_id == match.player2_id else False),
                score=match.player2_score if match.player2_score is not None else 0,
                sets=[match_set.player2_score for match_set in match.sets],
            ),
        )

        return match_schema

    # async def create_match(self, data: CreateMatchRequest):
    #     # Создание матча
    #     match = Match(player1_id=data.player1_id, player2_id=data.player2_id)
    #     id = await self.repo.create(match)

    #     # Создание пустых сетов
    #     match_sets = []
    #     for i in range(1, data.best_of + 1):
    #         match_set = MatchSet(
    #             match_id=match.id, set_number=i, player1_score=0, player2_score=0
    #         )
    #         match_sets.append(match_set)

    #     self.session.add_all(match_sets)
    #     await self.session.commit()

    #     return match.id

    # async def update_set(self, data: UpdateSetSchema):
    #     stmt = select(MatchSet).where(
    #         MatchSet.match_id == data.match_id, MatchSet.set_number == data.set_number
    #     )
    #     match_set = await self.session.scalar(stmt)
    #     if not match_set:
    #         return None

    #     match_set.player1_score = data.player1_score
    #     match_set.player2_score = data.player2_score
    #     match_set.winner_id = data.winner_id

    #     await self.session.commit()
