from telegram.ext import ContextTypes

from app.services.service_factory import ServiceFactory
from app.utils.channel import submission_publisher


async def process_submission_queue(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает очередь предложок, публикуя их в канал, если пришло их время.

    Args:
        context (ContextTypes.DEFAULT_TYPE): Контекст обработчика.
    """
    service_factory: ServiceFactory = context.bot_data["service_factory"]

    async with service_factory.create() as services:
        submission = await services.submissions.get_next_due_queued()

        if submission is None:
            return

        await submission_publisher(context, submission)
        await services.submissions.mark_published(submission)
