from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.container import ServiceContainer


class ServiceContext:
    """Контекст для работы с сервисами.

    Используется для управления жизненным циклом сессии.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> ServiceContainer:
        self.session = self.session_factory()
        return ServiceContainer(self.session)

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return

        if exc is not None:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()


class ServiceFactory:
    """Фабрика для создания контекста сервисов."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    def create(self) -> ServiceContext:
        return ServiceContext(self.session_factory)
