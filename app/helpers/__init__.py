from datetime import timedelta

from telegram.ext import ContextTypes


def format_publish_time_jst(publish_at) -> str:
    """Форматирует время публикации в JST (UTC+9) для отображения пользователю.

    Args:
        publish_at (_type_): Время публикации в UTC.

    Returns:
        str: Отформатированное время публикации в JST в виде строки "MM/DD HH:MM".
    """
    return (publish_at + timedelta(hours=9)).strftime("%m/%d %H:%M")


def clear_submission_data(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очищает данные, связанные с черновиком сабмишна, из user_data.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Контекст обработчика.
    """
    context.user_data.pop("submission_draft", None)
    context.user_data.pop("submission_awaiting_confirm", None)
