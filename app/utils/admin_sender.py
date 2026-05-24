from telegram import InlineKeyboardMarkup
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.database.models.submission import Submission, SubmissionMedia
from app.keyboards.submission import admin_submission_keyboard
from app.texts.messages import ModerationMessage


async def send_submission_to_all_admins(
    context: ContextTypes.DEFAULT_TYPE,
    submission: Submission,
) -> None:
    """
    Отправляет предложку всем администраторам для модерации.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Контекст обработчика.
        submission (Submission): Предложка для модерации.

    Raises:
        Exception: Если произошла ошибка при отправке.
    """
    submission_id = submission.id
    keyboard = admin_submission_keyboard(
        submission_id, queue_interval_minutes=settings.queue_interval_minutes
    )
    for admin_id in settings.admin_ids_list:
        try:
            await send_submission_to_admin(
                admin_id=admin_id,
                context=context,
                submission=submission,
                keyboard=keyboard,
            )
        except Exception as e:
            raise Exception(e)


async def send_submission_to_admin(
    admin_id: int,
    context: ContextTypes,
    submission: Submission,
    keyboard: InlineKeyboardMarkup,
) -> None:
    """
    Отправляет предложку конкретному администратору для модерации.

    Args:
        admin_id (int): ID администратора, которому отправляется предложка.
        context (ContextTypes): Контекст обработчика.
        submission (Submission): Предложка для модерации.
        keyboard (InlineKeyboardMarkup): Клавиатура с кнопками модерации.
    """
    media_items = submission.media_items

    author = submission.user.display_name
    user_text = submission.caption

    caption = ModerationMessage.NEW_SUBMISSION.format(author=author, user_text=user_text)

    # если одиночное медиа - отправляем с кнопками сразу
    if len(media_items) == 1:
        item = media_items[0]
        caption = caption
        send_method = get_send_method(context.bot, item.media_type)
        await send_method(
            chat_id=admin_id,
            **media_kwargs(item),
            caption=caption,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    else:
        # Медиагруппа — сначала все медиа, потом отдельным сообщением кнопки
        from telegram import InputMediaPhoto, InputMediaVideo

        input_media = []
        for i, item in enumerate(media_items):
            # Caption только на первом элементе группы
            item_caption = caption if i == 0 else None

            if item.media_type == "photo":
                input_media.append(
                    InputMediaPhoto(
                        media=item.file_id,
                        caption=item_caption,
                        parse_mode="HTML" if item_caption else None,
                    )
                )
            elif item.media_type == "video":
                input_media.append(
                    InputMediaVideo(
                        media=item.file_id,
                        caption=item_caption,
                        parse_mode="HTML" if item_caption else None,
                    )
                )
            # animation нельзя добавить в медиагруппу — пропускаем

        await context.bot.send_media_group(chat_id=admin_id, media=input_media)

        # кнопки модерации отдельным сообщением
        await context.bot.send_message(
            chat_id=admin_id,
            text=ModerationMessage.ABOVE,
            reply_markup=keyboard,
        )


def get_send_method(bot: ContextTypes.DEFAULT_TYPE.bot, media_type: str) -> callable:
    """
    Получает метод отправки для данного типа медиа.

    Args:
        bot (ContextTypes.DEFAULT_TYPE.bot): Экземпляр бота для доступа к методам отправки.
        media_type (str): Тип медиа.

    Raises:
        ValueError: Если тип медиа не поддерживается.

    Returns:
        callable: Метод отправки для данного типа медиа.
    """
    if media_type == "photo":
        return bot.send_photo
    elif media_type == "video":
        return bot.send_video
    elif media_type == "animation":
        return bot.send_animation
    raise ValueError(f"Unknown media_type {media_type}")


def media_kwargs(media_item: SubmissionMedia) -> dict:
    """
    Формирует словарь аргументов для метода отправки в зависимости от типа медиа.

    Args:
        media_item (SubmissionMedia): Элемент медиа для отправки.

    Raises:
        ValueError: Если тип медиа не поддерживается.

    Returns:
        dict: Словарь аргументов для метода отправки.
    """
    media_type = media_item.media_type
    file_id = media_item.file_id

    if media_type == "photo":
        return {"photo": file_id}
    elif media_type == "video":
        return {"video": file_id}
    elif media_type == "animation":
        return {"animation": file_id}
    raise ValueError(f"Unknown media_type {media_type}")
