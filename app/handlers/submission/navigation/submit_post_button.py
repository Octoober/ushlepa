from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.submission import submission_menu_keyboard
from app.schemas.submission_draft import SubmissionDraft
from app.states.user_states import UserState
from app.texts.messages import SubmissionMessages


async def submit_post_button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Срабатывает если юзер выбрал "предложить пост" в главном меню"""
    message = update.message

    if message is None:
        return

    context.user_data["submission_draft"] = SubmissionDraft(
        caption=None,
        media_items=[],
    )
    context.user_data.pop("submission_awaiting_confirm", None)

    await message.reply_text(
        SubmissionMessages.INSTRUCTION,
        reply_markup=submission_menu_keyboard(),
    )

    # переводим с состояние предложки.
    return UserState.SUBMISSION
