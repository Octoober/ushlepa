from typing import Literal, TypedDict


class MediaItemDraft(TypedDict):
    """Конкретный  медиа."""

    file_id: str
    media_type: Literal["photo", "video", "animation"]
    position: int


class SubmissionDraft(TypedDict):
    """Обертка для группы медиа."""

    caption: str | None
    media_items: list[MediaItemDraft]
