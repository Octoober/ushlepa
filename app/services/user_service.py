from dataclasses import dataclass

from app.config.settings import settings
from app.database.models import BotUser
from app.database.repositories.user_repository import UserRepository


@dataclass
class UserResult:
    user: BotUser
    is_created: bool


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_or_create_user(
        self,
        telegram_id: int,
        display_name: str | None,
        username: str | None,
    ) -> UserResult:
        user = await self.user_repo.get_by_telegram_id(telegram_id)

        role = "admin" if telegram_id in settings.admin_ids_list else "user"

        if user is not None:
            user.display_name = display_name
            user.username = username
            user.role = role

            return UserResult(user=user, is_created=False)

        await self.user_repo.create(
            telegram_id=telegram_id,
            display_name=display_name,
            username=username,
            role=role,
        )

        return UserResult(user=user, is_created=True)

    async def get_by_telegram_id(self, telegram_id: int) -> BotUser | None:
        return await self.user_repo.get_by_telegram_id(telegram_id)
