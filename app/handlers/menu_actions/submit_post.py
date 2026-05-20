from telegram import Update
from telegram.ext import ContextTypes

# from app.schemas.submission_draft import SubmissionDraft


async def handle_submit_post_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Срабатывает если юзер выбрал в майн меню "предложить пост"
    """
    message = update.message

    if message is None:
        return

    # context.user_data["mode"] = "waiting_submission"
    # context.user_data["submission_draft"] = SubmissionDraft(
    #     caprion=None,
    #     media_items=[],
    # )

    await message.reply_text("отправь картинку для предложки")
