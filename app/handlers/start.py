from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from app.middlewares.rate_limit import rate_limit

# from app.keyboards.main_menu import build_main_menu
from app.services.service_factory import ServiceFactory


@rate_limit(
    key="start", cooldown=2, warning_message="Слишком часто. Подожди {seconds} сек"
)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    message = update.effective_message

    if user is None or message is None:
        return

    service_factory: ServiceFactory = context.bot_data["service_factory"]

    async with service_factory.create() as service:
        result = await service.users.get_or_create_user(
            telegram_id=user.id,
            display_name=user.full_name,
            username=user.username,
        )

    if result.is_created:
        text = (
            f"Привет {user.first_name}! Ты новенький?\n"
            "Принимаю твои передачки в местный ПНД.\n"
            "Например: картинку, видео или гифку."
        )
    else:
        text = "Ты настоящий баклажан?"

    await message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
