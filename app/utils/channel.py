# Утилита для работы с каналом. Например отправляет предложку в канал


from html import escape

from telegram import InputMediaPhoto, InputMediaVideo
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.database.models.submission import Submission


async def submission_publisher(
    context: ContextTypes.DEFAULT_TYPE,
    submission: Submission,
) -> None:
    """
    Публикует предложку в канал.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Контекст обработчика.
        submission (Submission): Предложка для публикации.
    """
    db_user = submission.user

    if submission.is_anonymous:
        display_name = "анон"
    else:
        display_name = escape(db_user.display_name or "черкаш")

        if db_user.username:
            username = escape(db_user.username)
            display_name = f'<a href="https://t.me/{username}">{display_name}</a>'

    user_text = f"{escape(submission.caption)}\n\n" if submission.caption else ""
    bot_link = f'<a href="https://t.me/{settings.bot_name}">💬</a>' if settings.bot_name else "💬"
    caption = f"{user_text}{bot_link} {display_name}"

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
        parse_mode = "HTML" if item_caption else None

        if item.media_type == "photo":
            media_group.append(
                InputMediaPhoto(
                    media=item.file_id,
                    caption=item_caption,
                    parse_mode=parse_mode,
                )
            )

        elif item.media_type == "video":
            media_group.append(
                InputMediaVideo(
                    media=item.file_id,
                    caption=item_caption,
                    parse_mode=parse_mode,
                )
            )

    if not media_group:
        await context.bot.send_message(
            chat_id=settings.channel_name,
            text=caption,
            parse_mode="HTML",
        )
        return

    await context.bot.send_media_group(
        chat_id=settings.channel_name,
        media=media_group,
    )
