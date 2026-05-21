# from

from datetime import timedelta


def format_publish_time_jst(publish_at) -> str:
    return (publish_at + timedelta(hours=9)).strftime("%m/%d %H:%M")
