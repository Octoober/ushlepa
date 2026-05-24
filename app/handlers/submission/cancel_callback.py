from telegram import Update
from telegram.ext import ContextTypes

from app.schemas.submission_draft import SubmissionDraft
from app.texts.messages import SubmissionMessages

AWAITING_CONFIRM_KEY = "submission_awaiting_confirm"


async def submission_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработывает нажатия на кнопку отмены отправки предложки.

    Args:
        update (Update): Объект обновления от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст обработчика.
    """
    query = update.callback_query

    if query is None or context.user_data is None:
        return

    await query.answer()

    context.user_data["submission_draft"] = SubmissionDraft(
        caption=None,
        media_items=[],
    )
    context.user_data.pop(AWAITING_CONFIRM_KEY, None)

    await query.edit_message_text(SubmissionMessages.CANCELLED)
