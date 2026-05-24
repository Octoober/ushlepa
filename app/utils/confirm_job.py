from telegram.ext import CallbackContext, ContextTypes

from app.constants import (
    CONFIRM_BUTTONS_DELAY_SECOND,
    CONFIRM_BUTTONS_JOB_PREFIX,
    SUBMISSION_AWAITING_CONFIRM_KEY,
    SUBMISSION_DRAFT_KEY,
)
from app.keyboards.submission import user_submission_confirm_keyboard
from app.schemas.submission_draft import SubmissionDraft
from app.texts.messages import SubmissionMessages


async def show_confirm_buttons(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    reply_to_message_id: int | None = None,
) -> None:
    draft: SubmissionDraft | None = context.user_data.get(SUBMISSION_DRAFT_KEY)
    if not draft or not draft.get("media_items"):
        return

    context.user_data[SUBMISSION_AWAITING_CONFIRM_KEY] = True
    count = len(draft["media_items"])

    await context.bot.send_message(
        chat_id=chat_id,
        text=SubmissionMessages.MEDIA_RECEIVED.format(count=count),
        reply_markup=user_submission_confirm_keyboard(),
        reply_to_message_id=reply_to_message_id,
    )


async def _show_confirm_buttons_from_timer(context: CallbackContext) -> None:
    """Обёртка для run_once — берёт chat_id и last_message_id из draft."""
    draft: SubmissionDraft | None = context.user_data.get(SUBMISSION_DRAFT_KEY)
    last_message_id = draft.get("last_message_id") if draft else None

    await show_confirm_buttons(
        context,
        chat_id=context.job.chat_id,
        reply_to_message_id=last_message_id,
    )


def restart_confirm_buttons_timer(
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    user_id: int,
) -> None:
    if context.job_queue is None:
        raise RuntimeError("JobQueue is not available")

    job_name = make_confirm_buttons_job_name(chat_id=chat_id, user_id=user_id)

    for job in context.job_queue.get_jobs_by_name(job_name):
        try:
            job.schedule_removal()
        except Exception:
            pass

    context.job_queue.run_once(
        _show_confirm_buttons_from_timer,
        when=CONFIRM_BUTTONS_DELAY_SECOND,
        chat_id=chat_id,
        user_id=user_id,
        name=job_name,
    )


def make_confirm_buttons_job_name(chat_id: int, user_id: int) -> str:
    return f"{CONFIRM_BUTTONS_JOB_PREFIX}:{chat_id}:{user_id}"
