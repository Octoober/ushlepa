from collections.abc import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.handlers.submission.navigation.submit_post_button import (
    submit_post_button_handler,
)
from app.keyboards.main_menu import build_main_menu
from app.states.user_states import UserState
from app.texts.buttons import MainMenuButtons
from app.texts.messages import MainMenuMessages

MenuAction = Callable[
    [Update, ContextTypes.DEFAULT_TYPE],
    Awaitable[None],
]

MENU_ACTIONS: dict[str, MenuAction] = {
    MainMenuButtons.SUBMIT_POST: submit_post_button_handler,
}


async def main_menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Маршрутизатор для основного ReplyKey"""
    messgae = update.effective_message
    user = update.effective_user

    if messgae is None or messgae.text is None:
        return UserState.MAIN_MENU

    text = messgae.text.strip()
    action = MENU_ACTIONS.get(text)

    if action is not None:
        result = await action(update, context)
        return result if result is not None else UserState.MAIN_MENU

    is_admin = user.id in settings.admin_ids_list

    await messgae.reply_text(
        MainMenuMessages.UNKNOWN_COMMAND,
        reply_markup=build_main_menu(is_admin=is_admin),
    )

    return UserState.MAIN_MENU
