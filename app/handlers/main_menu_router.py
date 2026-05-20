from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.menu_actions.submit_post import handle_submit_post_button


async def main_menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    messgae = update.effective_message

    if messgae is None or messgae.text is None:
        return

    text = messgae.text.strip()

    if text == "предложить пост":
        await handle_submit_post_button(update, context)
    elif text == "профиль":
        pass
