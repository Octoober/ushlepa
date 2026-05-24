class StartMessages:
    GREETING_NEW = (
        "Привет {name}! Ты новенький?\n"
        "Принимаю твои передачки в местный ПНД.\n"
        "Например: картинку, видео или гифку."
    )
    GREETING_RETURNING = "Ты настоящий баклажан?"
    IS_ADMIN_SUFFIX = "\n\nкстати ты админ"


class MainMenuMessages:
    UNKNOWN_COMMAND = "Используй кнопки ниже 👇"


class SubmissionMessages:
    INSTRUCTION = "Отправь картинку, видео или гиф"
    MEDIA_RECEIVED = "Получино {count} медиа. Как будем публиковать?"
    SENT = "Предложка отправлена! Щпащибо"
    CANCELLED = "Ладно. В другой раз..."
    NO_MEDIA = "Нет медиа для отправки. Попробуй еще раз"
    PRESSED_BACK_BTN = "Возврат в главное меню"
    WRONG_INPUT = "Не понимаю. Пришли картинку, видео или гиф"
    WRONG_DRAFT = "Какие-то проблемы с сохранением черновика. Попробуй еще раз."
    WRONG_PARTS = "Странный запрос"


class ModerationMessage:
    NEW_SUBMISSION = "Новая предложка от: {author}\nТекст: {user_text}"
    ABOVE = "Предложка выше"
    QUEUED = "Добавлена в очередь"
    REMOVE_QUEUE = "Снята с очереди"
    REJECTED = "Отклонена"
    PUBLISHED = "Опубликована"
    NO_ACCESS = "Нет доступа"
    UNKNOWN_ACTION = "Неизвестное действие"


class CommonMessages:
    ERROR = "Что-то пошло не так. Попробуй еще раз."
    RATE_LIMIT_WARNING = "Сенпай, слишком быстро! Подожди еще {seconds} секунд."
