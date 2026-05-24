from datetime import timedelta, timezone

JST = timezone(timedelta(hours=9))


def format_publish_time(publish_at, tz=JST) -> str:
    """
    Форматирует время публикации в строку вида "MM/DD HH:MM" в заданной временной зоне.

    Args:
        publish_at (_type_): Дата и время публикации в виде объекта datetime.
        tz (_type_, optional): Временная зона для форматирования. Defaults to JST.

    Returns:
        str: Отформатированное время публикации в заданной временной зоне.
    """
    return publish_at.astimezone(tz).strftime("%m/%d %H:%M")
