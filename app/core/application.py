from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config.settings import settings
from app.database.manager import DatabaseManager
from app.handlers.start import start
from app.handlers.submission.admin_callbacks import submission_admin_callback
from app.handlers.submission.media_callbacks import (
    submission_cancel_callback,
    submission_confirm_callback,
)
from app.handlers.user_state_router import user_state_router
from app.jobs.submission_queue import process_submission_queue
from app.services.service_factory import ServiceFactory


class BotApplication:
    def __init__(self):
        self.db_manager = DatabaseManager(settings.database_url)
        self.application: Application | None = None

    def build(self) -> None:
        self.application = (
            ApplicationBuilder()
            .token(settings.bot_token)
            .post_init(self._on_startup)
            .post_shutdown(self._on_shutdown)
            .build()
        )

        self._register_services()
        self._register_handlers()

    def run(self) -> None:
        self.build()
        self.application.run_polling()

    def _register_services(self) -> None:
        self.application.bot_data["service_factory"] = ServiceFactory(
            self.db_manager.session_factory
        )

    def _register_handlers(self) -> None:
        self.application.add_handler(
            CommandHandler("start", start, filters=filters.ChatType.PRIVATE)
        )

        self.application.add_handler(
            CallbackQueryHandler(
                submission_confirm_callback,
                pattern=r"submission:confirm:",
            )
        )
        self.application.add_handler(
            CallbackQueryHandler(
                submission_cancel_callback,
                pattern=r"submission:cancel$",
            )
        )

        self.application.add_handler(
            CallbackQueryHandler(
                submission_admin_callback,
                pattern=r"moderate:",
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters.ChatType.PRIVATE & filters.ALL & ~filters.COMMAND,
                user_state_router,
            )
        )

    async def _on_startup(self, application: Application) -> None:
        await self.db_manager.init()
        await application.bot.delete_my_commands()

        if application.job_queue is None:
            raise RuntimeError("JobQueue is not available")

        application.job_queue.run_repeating(
            process_submission_queue,
            interval=60,
            first=10,
            name="submission_queue",
        )

    async def _on_shutdown(self, application: Application) -> None:
        await self.db_manager.close()
