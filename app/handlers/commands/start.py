from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.keyboards.main_menu import build_main_menu
from app.services.service_factory import ServiceFactory
from app.states.user_states import UserState
from app.texts.messages import CommonMessages, StartMessages
from app.utils.rate_limit import rate_limit
from app.utils.submission_draft import clear_submission_data
from app.utils.user_state import reset_user_state


@rate_limit(key="start", cooldown=30, warning_message=CommonMessages.RATE_LIMIT_WARNING)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Точка входа в бота. Вызывается при команде /start.

    Так же выполняет функцию регистрации пользователя в БД
    при первом запуске и сброса сессии при каждом запуске.
    """
    user = update.effective_user
    message = update.effective_message

    if user is None or message is None:
        return

    service_factory: ServiceFactory = context.bot_data["service_factory"]

    async with service_factory.create() as service:
        result = await service.users.get_or_create_user(
            telegram_id=user.id,
            display_name=user.full_name,
            username=user.username,
        )

    # не использовать полный сброс потому что это ломает rate_limit
    # context.user_data.clear()

    clear_submission_data(context)
    reset_user_state(context)

    is_admin = update.effective_user.id in settings.admin_ids_list

    if result.is_created:
        text = StartMessages.GREETING_NEW.format(name=user.first_name)
    else:
        text = StartMessages.GREETING_RETURNING

    if is_admin:
        text += StartMessages.IS_ADMIN_SUFFIX

    await message.reply_text(text=text, reply_markup=build_main_menu(is_admin=is_admin))

    # начинаем с главного меню
    return UserState.MAIN_MENU
