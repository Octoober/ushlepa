from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.keyboards.main_menu import build_main_menu
from app.states.user_states import UserState
from app.texts.buttons import SubmissionButtons
from app.texts.messages import SubmissionMessages


async def submission_menu_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    text = update.message.text

    if text == SubmissionButtons.BACK:
        # Полный сброс, если юзер отправил /start
        context.user_data.pop("submission_draft", None)
        context.user_data.pop("submission_awaiting_confirm", None)

        is_admin = update.effective_user.id in settings.admin_ids_list
        await update.message.reply_text(
            SubmissionMessages.PRESSED_BACK_BTN,
            reply_markup=build_main_menu(is_admin),
        )
        return UserState.MAIN_MENU

    await update.message.reply_text(
        SubmissionMessages.WRONG_INPUT,
    )
    return UserState.SUBMISSION
