from telegram import KeyboardButton, ReplyKeyboardMarkup

from app.texts.buttons import AdminMainMenuButtons, MainMenuButtons

USER_MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton(MainMenuButtons.SUBMIT_POST)],
        # [
        #     KeyboardButton(MainMenuButtons.GACHA),
        #     KeyboardButton(MainMenuButtons.MY_CARDS),
        # ],
        # [
        #     KeyboardButton(MainMenuButtons.BALANCE),
        #     KeyboardButton(MainMenuButtons.PROFILE),
        # ],
    ],
    resize_keyboard=True,
    is_persistent=False,
)

ADMIN_MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(AdminMainMenuButtons.QUEUE_POSTS)],
    ],
    resize_keyboard=True,
    is_persistent=False,
)


def build_main_menu(is_admin: bool) -> ReplyKeyboardMarkup:
    if is_admin:
        return ADMIN_MAIN_MENU
    return USER_MAIN_MENU
