from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

# from app.keyboards.main_menu import build_main_menu
from app.services.service_factory import ServiceFactory


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
        text = f"Привет {user.first_name}! Ты новый юзер и я добавил тебя в базу."
        await message.reply_text(f"привет {user.username}! ты новый юзер!")
    else:
        text = f"С возвращением {user.first_name}!"

    await message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
