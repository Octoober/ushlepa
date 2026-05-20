from telegram import BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.config import settings
from app.database.manager import DatabaseManager
from app.handlers.main_menu_router import main_menu_router
from app.handlers.start import start
from app.handlers.submission.admin_callbacks import submission_admin_callback
from app.handlers.submission.media_callbacks import (
    submission_cancel_callback,
    submission_confirm_callback,
)
from app.handlers.submission.media_handler import submission_media_handler
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
        self.application.add_handler(CommandHandler("start", start))
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                main_menu_router,
            )
        )
        self.application.add_handler(
            CallbackQueryHandler(
                submission_confirm_callback,
                pattern=r"^submission:confirm:",
            )
        )
        self.application.add_handler(
            CallbackQueryHandler(
                submission_cancel_callback,
                pattern=r"^submission:cancel:",
            )
        )
        self.application.add_handler(
            CallbackQueryHandler(
                submission_admin_callback,
                pattern=r"^moderate:",
            )
        )
        self.application.add_handler(
            MessageHandler(
                filters.PHOTO,
                submission_media_handler,
            )
        )

    async def _on_startup(self, application: Application) -> None:
        await self.db_manager.init()
        await application.bot.delete_my_commands()
        await application.bot.set_my_commands(
            commands=[
                BotCommand("start", "допустим старт"),
            ]
        )

    async def _on_shutdown(self, application: Application) -> None:
        await self.db_manager.close()
