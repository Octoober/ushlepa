from telegram.ext import ContextTypes

from app.schemas.submission_draft import MediaItemDraft, SubmissionDraft


def get_or_create_submission_draft(
    context: ContextTypes.DEFAULT_TYPE,
) -> SubmissionDraft:
    """
    Получает существующий черновик сабмишна из user_data или создает новый, если его нет.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Контекст обработчика, содержащий user_data.

    Returns:
        SubmissionDraft: Существующий или новый черновик сабмишна.
    """
    draft: SubmissionDraft | None = context.user_data.get("submission_draft")

    if draft is None:
        draft = SubmissionDraft(
            caption=None,
            media_items=[],
        )
        context.user_data["submission_draft"] = draft

    return draft


def extract_media_item(
    message,
    draft: SubmissionDraft,
) -> MediaItemDraft | None:
    """
    Извлекает медиа из сообщения и создает MediaItemDraft.

    Args:
        message (_type_): Сообщение Telegram, содержащее медиа.
        draft (SubmissionDraft): Черновик сабмишна.

    Returns:
        MediaItemDraft | None: Созданный черновик медиа или None, если медиа не найдено.
    """
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


def clear_submission_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очищает данные, связанные с черновиком сабмишна, из user_data.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Контекст обработчика.
    """
    context.user_data.pop("submission_draft", None)
    context.user_data.pop("submission_awaiting_confirm", None)
