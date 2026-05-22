from collections.abc import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.submission import submission_menu_keyboard
from app.states.user_states import UserState
from app.texts.buttons import MainMenuButtons

MenuAction = Callable[
    [Update, ContextTypes.DEFAULT_TYPE],
    Awaitable[None],
]


async def main_menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Маршрутизатор для основного ReplyKey"""
    message = update.effective_message
    if message is None or message.text is None:
        return

    if message.text == MainMenuButtons.SUBMIT_POST:
        # нажата кнопка "отправить предложку"
        context.user_data.clear()
        context.user_data["state"] = UserState.SUBMISSION

        await message.reply_text(
            "Отправь медиа для предложки",
            reply_markup=submission_menu_keyboard(),
        )
        return

    await message.reply_text("Выбери действие из меню")
