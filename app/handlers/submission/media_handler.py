from telegram import Update
from telegram.ext import ContextTypes

from app.constants import SUBMISSION_AWAITING_CONFIRM_KEY, SUBMISSION_DRAFT_KEY
from app.texts.messages import SubmissionMessages
from app.utils.confirm_job import restart_confirm_buttons_timer, show_confirm_buttons
from app.utils.submission_draft import extract_media_item, get_or_create_submission_draft


async def submission_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    tg_user = update.effective_user
    chat = update.effective_chat

    if message is None or tg_user is None or chat is None:
        return

    is_group = message.media_group_id is not None

    if is_group:
        # Медиагруппа — накапливаем все медиа через таймер
        if context.user_data.get(SUBMISSION_AWAITING_CONFIRM_KEY):
            return

        draft = get_or_create_submission_draft(context)
        media_item = extract_media_item(message, draft)
        if media_item is None:
            return

        if not draft.get("caption") and message.caption:
            draft["caption"] = message.caption

        draft["media_items"].append(media_item)
        draft["last_message_id"] = message.message_id  # обновляем каждый раз

        restart_confirm_buttons_timer(context, chat.id, tg_user.id)

    else:
        # Одиночное медиа — сразу показываем кнопки
        if context.user_data.get(SUBMISSION_AWAITING_CONFIRM_KEY):
            await message.reply_text(
                "Сначала подтверди или отмени предыдущую предложку 👆",
                reply_to_message_id=message.message_id,
            )
            return

        # Сбрасываем старый черновик — каждое одиночное медиа это новая предложка
        context.user_data.pop(SUBMISSION_DRAFT_KEY, None)
        draft = get_or_create_submission_draft(context)
        media_item = extract_media_item(message, draft)
        if media_item is None:
            await message.reply_text(SubmissionMessages.WRONG_INPUT)
            return

        if not draft.get("caption") and message.caption:
            draft["caption"] = message.caption

        draft["media_items"].append(media_item)

        await show_confirm_buttons(
            context,
            chat_id=chat.id,
            reply_to_message_id=message.message_id,
        )
