from telegram import Update
from telegram.ext import CallbackContext, ContextTypes

from app.keyboards.submission import user_submission_confirm_keyboard
from app.schemas.submission_draft import MediaItemDraft, SubmissionDraft


async def submission_media_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Обрабатывает файлы от юзера. Используется для предложки.

    Срабатывает только если "mode" установлен на waiting_submission.
    После срабатываения отображает inline кнопки
    которые формируются в build_submission_confirm_keyboard.
    """
    messgae = update.effective_message

    if messgae is None:
        return

    # if context.user_data.get("mode") != "waiting_submission":
    #     return

    context.user_data["submission_draft"] = SubmissionDraft(
        caprion=None,
        media_items=[],
    )
    draft: SubmissionDraft = context.user_data["submission_draft"]

    if draft is None:
        await messgae.reply_text("Нету draft")
        return

    if messgae.photo:
        file_id = messgae.photo[-1].file_id
        media_type = "photo"
    else:
        await messgae.reply_text("пока не поддерживает этот тип медиа")
        return

    # caption берется только из первого медиа
    if not draft.get("caption") and messgae.caption:
        draft["caption"] = messgae.caption

    draft["media_items"].append(
        MediaItemDraft(
            file_id=file_id,
            media_type=media_type,
            position=len(
                draft["media_items"],
            ),
        )
    )

    # сбрасываем предыдущий таймер если был
    old_job = context.user_data.get("confirm_job")
    if old_job:
        old_job.schedule_removal()

    # запускаем новый таймер через 0.5 сек
    job = context.job_queue.run_once(
        _show_confirm_buttons,
        when=0.5,
        chat_id=update.effective_chat.id,
        user_id=update.effective_user.id,
        data={"submission_draft": draft},
    )

    context.user_data["confirm_job"] = job


async def _show_confirm_buttons(context: CallbackContext) -> None:
    draft: SubmissionDraft = context.job.data["submission_draft"]
    count = len(draft["media_items"])
    text = f"получено {count} медиа. хочешь отправить предложку?"

    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text=text,
        reply_markup=user_submission_confirm_keyboard(),
    )
