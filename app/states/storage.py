from telegram.ext import ContextTypes

from app.states.user_states import UserState

STATE_KEY = "state"


def get_user_state(context: ContextTypes.DEFAULT_TYPE) -> UserState:
    raw_state = context.user_data.get(STATE_KEY)

    if raw_state is None:
        return UserState.MAIN_MENU

    try:
        return UserState(raw_state)
    except ValueError:
        return UserState.MAIN_MENU


def set_user_state(context: ContextTypes.DEFAULT_TYPE, state: UserState) -> None:
    context.user_data[STATE_KEY] = state.value


def reset_user_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    set_user_state(context, UserState.MAIN_MENU)
