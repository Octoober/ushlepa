from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.submission import submission_menu_keyboard
from app.states.user_states import UserState
from app.utils.user_state import set_user_state


async def entry_submission_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик для входа в режим предложки.
    Устанавливает состояние SUBMISSION и предлагает пользователю отправить медиа.
    """
    message = update.effective_message
    if message is None or message.text is None:
        return

    context.user_data.clear()
    set_user_state(context, UserState.SUBMISSION)

    await message.reply_text(
        "Отправь медиа для предложки",
        reply_markup=submission_menu_keyboard(),
    )
