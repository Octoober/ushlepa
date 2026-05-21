from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

from app.keyboards.submission import user_submission_confirm_keyboard
from app.schemas.submission_draft import MediaItemDraft, SubmissionDraft
from app.states.user_states import UserState
from app.texts.messages import SubmissionMessages

CONFIRM_BUTTONS_JOB_PREFIX = "submission_confirm_buttons"
CONFIRM_BUTTONS_DELAY_SECOND = 0.8
AWAITING_CONFIRM_KEY = "submission_awaiting_confirm"


async def submission_media_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обрабатывает медиа от пользователя в режиме предложки.

    Логика:
    1. Пользователь отправляет одно медиа или медиагруппу.
    2. Каждое медиа добавляется в submission_draft.
    3. После последнего медиа запускается короткий таймер.
    4. Когда медиагруппа закончилась и таймер тоже - отображаются inline-кнопки.
    """
    message = update.effective_message
    tg_user = update.effective_user
    chat = update.effective_chat

    if message is None or tg_user is None or chat is None:
        return UserState.SUBMISSION

    if context.user_data.get(AWAITING_CONFIRM_KEY):
        await message.reply_text("Сперва заверши неподтвержденную предложку.")
        return UserState.SUBMISSION

    draft = _get_or_create_submission_draft(context)
    media_item = _extract_media_item(message, draft)

    if media_item is None:
        await message.reply_text(SubmissionMessages.WRONG_INPUT)
        return UserState.SUBMISSION

    if not draft.get("caption") and message:
        draft["caption"] = message.caption

    draft["media_items"].append(media_item)

    _restart_confirm_buttons_timer(
        context=context,
        chat_id=chat.id,
        user_id=tg_user.id,
    )

    return UserState.SUBMISSION


async def _show_confirm_buttons(context: CallbackContext) -> None:
    draft: SubmissionDraft | None = context.user_data.get("submission_draft")

    if draft is None:
        return

    media_items = draft.get("media_items", [])

    if not media_items:
        return

    context.user_data[AWAITING_CONFIRM_KEY] = True

    count = len(media_items)
    text = SubmissionMessages.MEDIA_RECEIVED.format(count=count)

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=text,
        reply_markup=user_submission_confirm_keyboard(),
    )


def _get_or_create_submission_draft(
    context: ContextTypes.DEFAULT_TYPE,
) -> SubmissionDraft:
    draft: SubmissionDraft | None = context.user_data.get("submission_draft")

    if draft is None:
        draft = SubmissionDraft(
            caption=None,
            media_items=[],
        )
        context.user_data["submission_draft"] = draft

    return draft


def _extract_media_item(
    message,
    draft: SubmissionDraft,
) -> MediaItemDraft | None:
    if message.photo:
        file_id = message.photo[-1].file_id
        media_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        media_type = "video"
    elif message.animation:
        file_id = message.animation.file_id
        media_type = "animation"
    else:
        return None

    return MediaItemDraft(
        file_id=file_id,
        media_type=media_type,
        position=len(
            draft["media_items"],
        ),
    )


def _make_confirm_buttons_job_name(chat_id: int, user_id: int) -> str:
    return f"{CONFIRM_BUTTONS_JOB_PREFIX}:{chat_id}:{user_id}"


def _restart_confirm_buttons_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> None:
    if context.job_queue is None:
        raise RuntimeError("JobQueue is not available")

    job_name = _make_confirm_buttons_job_name(
        chat_id=chat_id,
        user_id=user_id,
    )

    for job in context.job_queue.get_jobs_by_name(job_name):
        try:
            job.schedule_removal()
        except Exception:
            # TODO: нужно найти конкретный exception для отлова ошибок job
            pass

    context.job_queue.run_once(
        _show_confirm_buttons,
        when=CONFIRM_BUTTONS_DELAY_SECOND,
        chat_id=chat_id,
        user_id=user_id,
        name=job_name,
    )
