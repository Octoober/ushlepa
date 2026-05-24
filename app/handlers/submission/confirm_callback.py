from telegram import Update
from telegram.ext import ContextTypes

from app.constants import SUBMISSION_AWAITING_CONFIRM_KEY, SUBMISSION_DRAFT_KEY
from app.services.service_factory import ServiceFactory
from app.texts.messages import SubmissionMessages
from app.utils.admin_sender import send_submission_to_all_admins
from app.utils.session import reset_user_session_to_main_menu


async def submission_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработывает нажатия на кнопки подтверждения отправки предложки.

    Например если пользователь нажал "отправить от моего имени" или
    "отправить анонимно" или "отмена" то этот колбек сработает.
    """
    query = update.callback_query
    tg_user = update.effective_user

    if tg_user is None or query is None:
        return

    await query.answer()

    draft = context.user_data.get(SUBMISSION_DRAFT_KEY)
    parts = (query.data or "").split(":")

    if parts is None or len(parts) != 3:
        await query.edit_message_text(SubmissionMessages.WRONG_PARTS)
        return

    # формат callback_data: submission:confirm:public или submission:confirm:anon
    # или submission:cancel
    entity, action, visibility = parts

    # если черновика нет, либо отсутствует media_items.
    # такое может быть если бот был перезапущен а юзер нажал по устаревшим inline.
    if not draft or not draft.get("media_items"):
        await reset_user_session_to_main_menu(
            update=update,
            context=context,
            text="бот был перезапущен. сессия зажарилась. попробуй еще раз 🙏",
        )
        return

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
    context.user_data.pop(SUBMISSION_DRAFT_KEY, None)
    context.user_data.pop(SUBMISSION_AWAITING_CONFIRM_KEY, None)

    # отправляем предложку админам
    await send_submission_to_all_admins(
        context=context,
        submission=submission,
    )

    await query.edit_message_text(SubmissionMessages.SENT)
