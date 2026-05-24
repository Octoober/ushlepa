from collections.abc import Awaitable, Callable
from functools import wraps
from time import monotonic

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
    warning_cooldown: float = 5,
) -> Callable[[HandlerFunc], HandlerFunc]:
    """
    Декоратор для ограничения частоты вызовов обработчика.

    Args:
        key (str): ключ для хранения времени последнего вызова в user_data.
         Обычно это может быть идентификатор пользователя.
        cooldown (float): минимальное время в секундах между вызовами обработчика для одного ключа.
        warning_message (str | None, optional): Сообщение предупреждения. Defaults to None.
        warning_cooldown (float, optional): Время в секундах между показами предупреждений.
         Defaults to 5.

    Returns:
        Callable[[HandlerFunc], HandlerFunc]: _description_
    """

    def decorator(func: HandlerFunc) -> HandlerFunc:
        @wraps(func)
        async def wrapper(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
        ) -> None:
            """
            Обертка для обработчика.

            Args:
                update (Update): Телеграм-апдейт, который вызвал обработчик.
                context (ContextTypes.DEFAULT_TYPE): Контекст обработчика.
            """
            now = monotonic()

            rate_limit_key = f"rate_limit:{key}"
            warning_key = f"rate_limit_warning:{key}"

            last_action_at = context.user_data.get(rate_limit_key)

            if last_action_at is not None:
                passed = now - last_action_at

                if passed < cooldown:
                    last_warning_at = context.user_data.get(warning_key)

                    should_warn = (
                        last_warning_at is None or now - last_warning_at >= warning_cooldown
                    )

                    if should_warn and warning_message:
                        message = update.effective_message

                        if message is not None:
                            remaining = int(cooldown - passed)

                            await message.reply_text(warning_message.format(seconds=remaining))

                        context.user_data[warning_key] = now

                    return

            context.user_data[rate_limit_key] = now

            await func(update, context)

        return wrapper

    return decorator
