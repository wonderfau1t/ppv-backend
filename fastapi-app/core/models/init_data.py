import random

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Match, MatchSet, UserAuth, UserData
from core.repositories import MatchRepository, UserRepository
from core.utils.bcrypt import hash_password

fake = Faker("ru_RU")


async def create_demo_data(session: AsyncSession):
    user_repo = UserRepository(session)
    match_repo = MatchRepository(session)

    existing_users = await user_repo.list_of_user_auth()
    if existing_users:
        print("Таблица не пуста — отмена генерации.")
        return

    print("Создание 50 пользователей...")

    users: list[int] = []

    for i in range(50):
        fn = fake.first_name_male()
        ln = fake.last_name_male()
        mn = fake.middle_name_male()

        user = UserData(
            first_name=fn,
            middle_name=mn,
            last_name=ln,
            user_auth=UserAuth(
                login=f"user{i}",
                password_hash=hash_password("test"),
            ),
        )

        uid = await user_repo.create(user)
        users.append(uid)

    print("Создание случайных матчей...")

    for _ in range(150):
        p1, p2 = random.sample(users, 2)

        sets = []
        p1_total = 0
        p2_total = 0
        winner = None

        for set_num in range(1, 4):
            p1_score = random.randint(5, 15)
            p2_score = random.randint(5, 15)

            p1_total += p1_score > p2_score
            p2_total += p2_score > p1_score

            set_winner = p1 if p1_score > p2_score else p2

            sets.append(
                MatchSet(
                    set_number=set_num,
                    player1_score=p1_score,
                    player2_score=p2_score,
                    winner_id=set_winner,
                )
            )

        winner = p1 if p1_total > p2_total else p2
        duration = random.randint(10, 40)

        match = Match(
            player1_id=p1,
            player2_id=p2,
            player1_score=p1_total,
            player2_score=p2_total,
            winner_id=winner,
            duration_in_minutes=duration,
            sets=sets,
        )

        await match_repo.create_with_stats(match)

    print("Генерация завершена.")
