from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.models.base import Base


class DatabaseManager:
    def __init__(self, database_url: str, echo: bool = False):
        self.engine: AsyncSession = create_async_engine(url=database_url, echo=echo)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def init(self) -> None:
        import app.database.models  # noqa: F401

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()
