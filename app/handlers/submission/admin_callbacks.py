from telegram import Update
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.handlers.submission.submission_publisher import publish_submission_to_channel
from app.helpers import format_publish_time_jst
from app.services.service_factory import ServiceFactory
from app.texts.messages import ModerationMessage


async def submission_admin_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Управление предложкой со стороны админа."""
    query = update.callback_query
    user = update.effective_user

    if query is None or user is None or query.data is None:
        return

    await query.answer()

    if user.id not in settings.admin_ids_list:
        await query.answer(ModerationMessage.NO_ACCESS, show_alert=True)
        return

    _, submission_id_str, action = query.data.split(":")

    if action not in {"queue", "publish", "reject", "cancel"}:
        await query.answer(ModerationMessage.UNKNOWN_ACTION, show_alert=True)
        return

    submission_id = int(submission_id_str)

    service_factory: ServiceFactory = context.bot_data["service_factory"]

    async with service_factory.create() as services:
        if action == "queue":
            publish_at = await services.submissions.queue(submission_id)
            status_text = (
                f"{ModerationMessage.QUEUED} {format_publish_time_jst(publish_at)}"
            )

        elif action == "publish":
            submission = await services.submissions.get_for_publication(submission_id)
            await publish_submission_to_channel(context, submission)
            await services.submissions.mark_published(submission)
            status_text = ModerationMessage.PUBLISHED

        elif action == "reject":
            await services.submissions.reject(submission_id)
            status_text = ModerationMessage.REJECTED

        elif action == "cancel":
            await services.submissions.cancel(submission_id)
            status_text = ModerationMessage.REMOVE_QUEUE

        else:
            await query.answer(ModerationMessage.UNKNOWN_ACTION, show_alert=True)
            return

    await query.edit_message_reply_markup(reply_markup=None)

    if query.message is not None:
        await query.message.reply_text(
            f"Предложка #{submission_id}: {status_text}\n",
        )
