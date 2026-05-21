from html import escape

from telegram import InputMediaPhoto, InputMediaVideo, Update
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.database.models.submission import Submission
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
    submission_id = int(submission_id_str)

    service_factory: ServiceFactory = context.bot_data["service_factory"]

    async with service_factory.create() as services:
        if action == "queue":
            await services.submissions.queue(submission_id)
            status_text = ModerationMessage.QUEUED

        elif action == "publish":
            submission = await services.submissions.publish(submission_id)
            await publish_submission_to_channel(context, submission)
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


async def publish_submission_to_channel(
    context: ContextTypes.DEFAULT_TYPE,
    submission: Submission,
) -> None:

    db_user = submission.user

    if submission.is_anonymous:
        display_name = "анон"
    else:
        display_name = escape(db_user.display_name or "черкаш")
        if db_user.username:
            username = db_user.username
            display_name = f'<a href="https://t.me/{username}">{display_name}</a>'

    user_text = f"{escape(submission.caption)}\n\n" if submission.caption else ""
    caption = f"{user_text}💬 {display_name}"

    media_items = submission.media_items

    if len(media_items) == 1:
        item = media_items[0]

        if item.media_type == "photo":
            await context.bot.send_photo(
                chat_id=settings.channel_name,
                photo=item.file_id,
                caption=caption,
                parse_mode="HTML",
            )
            return

        if item.media_type == "video":
            await context.bot.send_video(
                chat_id=settings.channel_name,
                video=item.file_id,
                caption=caption,
                parse_mode="HTML",
            )
            return

        if item.media_type == "animation":
            await context.bot.send_animation(
                chat_id=settings.channel_name,
                animation=item.file_id,
                caption=caption,
                parse_mode="HTML",
            )
            return

    media_group = []

    for index, item in enumerate(media_items):
        item_caption = caption if index == 0 else None

        if item.media_type == "photo":
            media_group.append(
                InputMediaPhoto(
                    media=item.file_id,
                    caption=item_caption,
                )
            )

        elif item.media_type == "video":
            media_group.append(
                InputMediaVideo(
                    media=item.file_id,
                    caption=item_caption,
                )
            )

    await context.bot.send_media_group(
        chat_id=settings.channel_name,
        media=media_group,
        parse_mode="HTML",
    )
