from telegram import Message, Update
from telegram.ext import ContextTypes

from app.keyboards.main_menu import build_main_menu


async def reset_user_session_to_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    *,
    is_admin: bool = False,
    remove_inline_keyboard: bool = True,
) -> None:
    """
    Сбрасывает сессию пользователя и возвращает его в главное меню.

    Используется после перезапуска бота, когда состояние в user_data
    могло устареть и больше не соответствует текущему шагу пользователя.

    Args:
        update (Update): Телеграм-апдейт, который вызвал сброс сессии.
        context (ContextTypes.DEFAULT_TYPE): Контекст приложения.
        text (str): Текст сообщения для пользователя.
        is_admin (bool, optional): Является ли пользователь администратором. Defaults to False.
        remove_inline_keyboard (bool, optional): Удалять ли inline клавиатуру. Defaults to True.
    """
    context.user_data.clear()
    query = update.callback_query
    if query is not None:
        await query.answer()
        if query.message is None:
            return

        message: Message = query.message

        if remove_inline_keyboard:
            await message.edit_reply_markup(reply_markup=None)

        await message.reply_text(text, reply_markup=build_main_menu(is_admin))
        return

    message: Message = update.effective_message
    if message is None:
        return

    await message.reply_text(text, reply_markup=build_main_menu(is_admin))
