from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from app.texts.buttons import ModerationButtons, SubmissionButtons


def user_submission_confirm_keyboard() -> InlineKeyboardMarkup:
    """Инлайн кнопки для юзера.

    Returns:
        InlineKeyboardMarkup: Инлайн кнопки.
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=SubmissionButtons.SEND_PUBLIC,
                    callback_data="submission:confirm:public",
                )
            ],
            [
                InlineKeyboardButton(
                    text=SubmissionButtons.SEND_ANON,
                    callback_data="submission:confirm:anon",
                )
            ],
            [
                InlineKeyboardButton(
                    text=SubmissionButtons.CANCEL,
                    callback_data="submission:cancel",
                )
            ],
        ]
    )


def admin_submission_keyboard(submission_id: int) -> InlineKeyboardMarkup:
    """Инлайн кнопки для модерации предложки.

    Args:
        submission_id (int): ID конкретной предложки.

    Returns:
        InlineKeyboardMarkup: Инлайн кнопки.
    """
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=ModerationButtons.QUEUE,
                    callback_data=f"moderate:{submission_id}:queue",
                )
            ],
            [
                InlineKeyboardButton(
                    text=ModerationButtons.PUBLISH_NOW,
                    callback_data=f"moderate:{submission_id}:publish",
                )
            ],
            [
                InlineKeyboardButton(
                    text=ModerationButtons.REJECT,
                    callback_data=f"moderate:{submission_id}:reject",
                )
            ],
        ]
    )


def submission_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура в режиме предложки.

    Returns:
        ReplyKeyboardMarkup: Кнопки для меню.
    """
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(SubmissionButtons.BACK)],
        ],
        resize_keyboard=True,
    )
