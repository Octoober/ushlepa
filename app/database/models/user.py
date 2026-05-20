from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .submission import Submission


class BotUser(BaseModel):
    __tablename__ = "bot_user"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(
        String(20), default="user", nullable=False, index=True
    )
    is_banned: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )

    submissions: Mapped[list[Submission]] = relationship(back_populates="user")
