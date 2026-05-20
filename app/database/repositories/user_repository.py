from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import BotUser


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> BotUser | None:
        stmt = select(BotUser).where(BotUser.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        display_name: str,
        username: str | None,
        role: str,
    ) -> BotUser:
        user = BotUser(
            telegram_id=telegram_id,
            display_name=display_name,
            username=username,
            role=role,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create(
        self,
        telegram_id: int,
        full_name: str,
        username: str | None,
    ) -> BotUser:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.create(telegram_id, full_name, username)
        return user
