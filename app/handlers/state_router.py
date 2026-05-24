from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.handlers.main_menu_router import main_menu_router
from app.handlers.submission.media_handler import submission_media_handler
from app.keyboards.main_menu import build_main_menu
from app.states.user_states import UserState
from app.texts.buttons import SubmissionButtons
from app.texts.messages import SubmissionMessages
from app.utils.user_state import get_user_state


async def state_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    state = get_user_state(context)

    if message.text == SubmissionButtons.BACK:
        context.user_data.clear()
        await message.reply_text(
            "Возврат в главное меню",
            reply_markup=build_main_menu(is_admin=False),
        )
        return

    if state == UserState.SUBMISSION:
        if message.photo or message.video or message.animation:
            await submission_media_handler(update, context)
            return
        await update.message.reply_text(SubmissionMessages.WRONG_INPUT)
        return

    if message.photo or message.video or message.animation:
        is_admin = update.effective_user.id in settings.admin_ids_list
        await message.reply_text(
            "Хочешь предложить пост? Нажми кнопку «Предложить пост» 👇",
            reply_markup=build_main_menu(is_admin=is_admin),
        )
        return

    await main_menu_router(update, context)
