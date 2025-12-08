from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Match, MatchSet, UserAuth, UserData, UserStats
from core.repositories import MatchRepository, UserRepository
from core.utils.bcrypt import hash_password


async def create_demo_data(session: AsyncSession):
    user_repo = UserRepository(session)
    match_repo = MatchRepository(session)

    is_filled = await user_repo.list_of_user_auth()
    if is_filled:
        print("Таблица не пустая. Нельзя заполнить демо данными")
        return

    user1 = UserData(
        first_name="Dmitrii",
        middle_name="Andreevich",
        last_name="Itigechev",
        user_auth=UserAuth(login="dima", password_hash=hash_password("test")),
    )
    user2 = UserData(
        first_name="Artemii",
        middle_name="Igorevich",
        last_name="Sviridov",
        user_auth=UserAuth(login="tema", password_hash=hash_password("test")),
    )

    print("Добавление пользователей...")
    user1_id = await user_repo.create(user1)
    user2_id = await user_repo.create(user2)

    match1 = Match(
        player1_id=user1_id,
        player2_id=user2_id,
        player1_score=2,
        player2_score=1,
        winner_id=user1_id,
        duration_in_minutes=21,
        sets=[
            MatchSet(
                set_number=1, player1_score=11, player2_score=5, winner_id=user1_id
            ),
            MatchSet(
                set_number=2, player1_score=11, player2_score=13, winner_id=user2_id
            ),
            MatchSet(
                set_number=3, player1_score=11, player2_score=2, winner_id=user1_id
            ),
        ],
    )
    match2 = Match(
        player1_id=user1_id,
        player2_id=user2_id,
        player1_score=1,
        player2_score=2,
        winner_id=user2_id,
        duration_in_minutes=25,
        sets=[
            MatchSet(
                set_number=1, player1_score=5, player2_score=11, winner_id=user2_id
            ),
            MatchSet(
                set_number=2, player1_score=11, player2_score=13, winner_id=user2_id
            ),
            MatchSet(
                set_number=3, player1_score=11, player2_score=2, winner_id=user1_id
            ),
        ],
    )

    print("Добавление матчей...")
    await match_repo.create(match1)
    await match_repo.create(match2)

    user1_stats = UserStats(
        id=user1.id,
        amateur_games_count=2,
        tournament_games_count=0,
        wins_count=1,
        losses_count=1,
        average_match_duration=23,
        average_time_to_point=12,
        total_matches_duration=46,
    )

    user2_stats = UserStats(
        id=user2.id,
        amateur_games_count=2,
        tournament_games_count=0,
        wins_count=1,
        losses_count=1,
        average_match_duration=23,
        average_time_to_point=10,
        total_matches_duration=46,
    )

    print("Сохранение статистики")
    await user_repo.update_stats(user1_stats)
    await user_repo.update_stats(user2_stats)
