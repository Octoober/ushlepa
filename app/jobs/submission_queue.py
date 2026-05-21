from telegram.ext import ContextTypes

from app.handlers.submission.submission_publisher import publish_submission_to_channel
from app.services.service_factory import ServiceFactory


async def process_submission_queue(context: ContextTypes.DEFAULT_TYPE) -> None:
    service_factory: ServiceFactory = context.bot_data["service_factory"]

    async with service_factory.create() as services:
        submission = await services.submissions.get_next_due_queued()

        if submission is None:
            return

        await publish_submission_to_channel(context, submission)
        await services.submissions.mark_published(submission)
