from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.config.settings import settings
from app.database.models.submission import Submission, SubmissionMedia
from app.keyboards.submission import admin_submission_keyboard
from app.schemas.submission_draft import SubmissionDraft
from app.services.service_factory import ServiceFactory
from app.states.user_states import UserState
from app.texts.messages import ModerationMessage, SubmissionMessages

AWAITING_CONFIRM_KEY = "submission_awaiting_confirm"


async def submission_confirm_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Обработывает нажатия на кнопки подтверждения отправки предложки.

    Например если пользователь нажал "отправить от моего имени" или
    "отправить анонимно" или "отмена" то этот колбек сработает.
    """
    query = update.callback_query
    tg_user = update.effective_user

    if tg_user is None or query is None:
        return

    await query.answer()

    draft = context.user_data.get("submission_draft")
    parts = (query.data or "").split(":")

    if parts is None or len(parts) != 3:
        await query.edit_message_text(SubmissionMessages.WRONG_PARTS)
        return UserState.SUBMISSION

    # формат callback_data: submission:confirm:public или submission:confirm:anon
    # или submission:cancel
    entity, action, visibility = parts

    # если черновика нет, либо отсутствует media_items
    if not draft or not draft.get("media_items"):
        await query.edit_message_text(SubmissionMessages.WRONG_DRAFT)
        return UserState.SUBMISSION

    is_anonymous = visibility == "anon"
    service_factory: ServiceFactory = context.bot_data["service_factory"]

    async with service_factory.create() as service:
        user_result = await service.users.get_or_create_user(
            telegram_id=tg_user.id,
            display_name=tg_user.full_name,
            username=tg_user.username,
        )

        db_user = user_result.user

        submission = await service.submissions.create_from_draft(
            user_id=db_user.id,
            draft=draft,
            is_anonymous=is_anonymous,
        )

    # создаем новый draft чтобы не ломать текущий контекст
    context.user_data["submission_draft"] = SubmissionDraft(
        caption=None,
        media_items=[],
    )
    context.user_data.pop(AWAITING_CONFIRM_KEY, None)

    # отправляем предложку админам
    await _send_to_all_admins(
        context=context,
        submission=submission,
    )

    await query.edit_message_text(SubmissionMessages.SENT)

    return UserState.SUBMISSION


async def submission_cancel_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["submission_draft"] = SubmissionDraft(
        caption=None,
        media_items=[],
    )
    context.user_data.pop(AWAITING_CONFIRM_KEY, None)

    await query.edit_message_text(SubmissionMessages.CANCELLED)
    return UserState.SUBMISSION


async def _send_to_all_admins(
    context: ContextTypes.DEFAULT_TYPE,
    submission: Submission,
) -> None:
    """Перебирает всех админов из .env и рассылает предложку."""
    submission_id = submission.id
    keyboard = admin_submission_keyboard(submission_id)
    for admin_id in settings.admin_ids_list:
        try:
            await _send_to_admin(
                admin_id=admin_id,
                context=context,
                submission=submission,
                keyboard=keyboard,
            )
        except Exception as e:
            raise Exception(e)


async def _send_to_admin(
    admin_id: int,
    context: ContextTypes,
    submission: Submission,
    keyboard: InlineKeyboardMarkup,
) -> None:
    media_items = submission.media_items

    author = submission.user.display_name
    user_text = submission.caption

    caption = ModerationMessage.NEW_SUBMISSION.format(
        author=author, user_text=user_text
    )

    # если одиночное медиа - отправляем с кнопками сразу
    if len(media_items) == 1:
        item = media_items[0]
        caption = caption
        send_method = _get_send_method(context.bot, item.media_type)
        await send_method(
            chat_id=admin_id,
            **_media_kwargs(item),
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


def _get_send_method(bot, media_type: str):
    if media_type == "photo":
        return bot.send_photo
    elif media_type == "video":
        return bot.send_video
    elif media_type == "animation":
        return bot.send_animation
    raise ValueError(f"Unknown media_type {media_type}")


def _media_kwargs(media_item: SubmissionMedia) -> dict:
    media_type = media_item.media_type
    file_id = media_item.file_id

    if media_type == "photo":
        return {"photo": file_id}
    elif media_type == "video":
        return {"video": file_id}
    elif media_type == "animation":
        return {"animation": file_id}
    raise ValueError(f"Unknown media_type {media_type}")
