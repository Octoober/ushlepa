from collections.abc import Awaitable, Callable
from functools import wraps
from time import time

from telegram import Update
from telegram.ext import ContextTypes

HandlerFunc = Callable[
    [Update, ContextTypes.DEFAULT_TYPE],
    Awaitable[None],
]


def rate_limit(
    *,
    key: str,
    cooldown: float,
    warning_message: str | None = None,
) -> Callable[[HandlerFunc], HandlerFunc]:
    """
    Декоратор для ограничения частоты вызовов обработчика.

    Args:
        key: уникальный ключ для хранения времени последнего вызова.
        cooldown: минимальный интервал в секундах между вызовами.
        warning_message: сообщение пользователю при превышении лимита.
            Поддерживает {seconds} для отображения оставшегося времени.
    """

    def decorator(func: HandlerFunc) -> HandlerFunc:
        @wraps(func)
        async def wrapper(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
        ):
            now = time()
            rate_limit_key = f"rate_limit:{key}"
            last_action_at = context.user_data.get(rate_limit_key)

            if last_action_at is not None:
                passed = now - last_action_at

                if passed < cooldown:
                    if warning_message:
                        message = update.effective_message
                        if message is not None:
                            remaining = int(cooldown - passed)
                            await message.reply_text(warning_message.format(seconds=remaining))
                    return

            context.user_data[rate_limit_key] = now
            return await func(update, context)

        return wrapper

    return decorator
