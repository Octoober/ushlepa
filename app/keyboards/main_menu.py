from telegram import KeyboardButton, ReplyKeyboardMarkup

from app.database.models import BotUser

USER_MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("предложить пост")],
        [KeyboardButton("профиль")],
    ],
    resize_keyboard=True,
    is_persistent=False,
)

ADMIN_MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("предложить пост")],
        [KeyboardButton("очередь постов")],
    ],
    resize_keyboard=True,
    is_persistent=False,
)


def build_main_menu(user: BotUser) -> ReplyKeyboardMarkup:
    if user.role == "admin":
        return ADMIN_MAIN_MENU
    return USER_MAIN_MENU
