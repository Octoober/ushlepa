from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .user import BotUser


class Submission(BaseModel):
    __tablename__ = "submissions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("bot_user.id"), nullable=False, index=True
    )
    caption: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_anonymous: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
    )
    user: Mapped[BotUser] = relationship(back_populates="submissions")
    media_items: Mapped[list[SubmissionMedia]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionMedia.position",
    )
    publish_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )


class SubmissionMedia(BaseModel):
    __tablename__ = "submission_media"

    submission_id: Mapped[int] = mapped_column(
        ForeignKey("submissions.id"), nullable=False, index=True
    )
    file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submission: Mapped[Submission] = relationship(back_populates="media_items")
