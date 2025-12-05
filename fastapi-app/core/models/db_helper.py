from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core import settings


class DBHelper:
    def __init__(self, url: str, echo: bool = False, echo_pool: bool = False) -> None:
        self.engine = create_async_engine(url=url, echo=echo, echo_pool=echo_pool)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def session_getter(self):
        async with self.session_factory() as session:
            yield session


db_helper = DBHelper(
    url=str(settings.db), echo=settings.db.echo, echo_pool=settings.db.echo_pool
)
 