from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.main_menu_router import main_menu_router
from app.handlers.submission.media_handler import submission_media_handler
from app.keyboards.main_menu import build_main_menu
from app.states.user_states import UserState
from app.texts.buttons import SubmissionButtons
from app.texts.messages import SubmissionMessages


async def user_state_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    state = context.user_data.get("state")

    if message.text == SubmissionButtons.BACK:
        context.user_data.clear()
        await message.reply_text(
            "Возврат в главное меню", reply_markup=build_main_menu(is_admin=False)
        )
        return

    if state == UserState.SUBMISSION:
        if message.photo or message.video or message.animation:
            await submission_media_handler(update, context)
            return

        await update.message.reply_text(SubmissionMessages.WRONG_INPUT)
        return

    if message.photo or message.video or message.animation:
        text = (
            "Похоже бот был перезапущен и твоя старая сессия сломалась.\n"
            "Попробуй начать заново"
        )
        await message.reply_text(
            text,
            reply_markup=build_main_menu(False),
        )
        return

    await main_menu_router(update, context)
