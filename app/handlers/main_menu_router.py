from collections.abc import Awaitable, Callable

from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.submission.entry import entry_submission_handler
from app.texts.buttons import MainMenuButtons

MenuAction = Callable[
    [Update, ContextTypes.DEFAULT_TYPE],
    Awaitable[None],
]


async def main_menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Маршрутизатор для основного меню.

    Принимает входящее сообщение и в зависимости от его текста вызывает соответствующий обработчик.
    Например, если пользователь нажал кнопку "Предложить пост", то
    вызывается entry_submission_handler
    """
    message = update.effective_message
    if message is None or message.text is None:
        return

    if message.text == MainMenuButtons.SUBMIT_POST:
        await entry_submission_handler(update, context)
        return

    await message.reply_text("Выбери действие из меню")
