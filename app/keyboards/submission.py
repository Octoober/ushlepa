from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def user_submission_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="отправить от моего имени",
                    callback_data="submission:confirm:public",
                )
            ],
            [
                InlineKeyboardButton(
                    text="отправить анонимно",
                    callback_data="submission:confirm:anon",
                )
            ],
            [
                InlineKeyboardButton(
                    text="отмена",
                    callback_data="submission:cancel",
                )
            ],
        ]
    )


def admin_submission_keyboard(submission_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="в очередь",
                    callback_data=f"moderate:{submission_id}:queue",
                )
            ],
            [
                InlineKeyboardButton(
                    text="опубликовать",
                    callback_data=f"moderate:{submission_id}:publish",
                )
            ],
            [
                InlineKeyboardButton(
                    text="отклонить",
                    callback_data=f"moderate:{submission_id}:reject",
                )
            ],
        ]
    )
