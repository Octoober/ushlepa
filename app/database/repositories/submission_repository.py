from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.submission import Submission, SubmissionMedia
from app.schemas.submission_draft import MediaItemDraft


class SubmissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        caption: str | None,
        is_anonymous: bool,
        media_items: list[MediaItemDraft],  # ← словари из draft
    ) -> Submission:
        submission = Submission(
            user_id=user_id,
            caption=caption,
            is_anonymous=is_anonymous,
            status="pending",
            # media_items сюда НЕ передаём
        )
        self.session.add(submission)
        await self.session.flush()

        for item in media_items:
            self.session.add(
                SubmissionMedia(
                    submission_id=submission.id,
                    file_id=item["file_id"],
                    media_type=item["media_type"],
                    position=item["position"],
                )
            )

        await self.session.flush()
        return await self.get_by_id(submission.id)

    async def get_by_id(self, submission_id: int) -> Submission | None:
        stmt = (
            select(Submission)
            .options(
                selectinload(Submission.media_items),
                selectinload(Submission.user),
            )
            .where(Submission.id == submission_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, submission_id: int, new_status: str) -> None:
        submission = await self.get_by_id(submission_id)
        if submission is None:
            return
        submission.status = new_status
        await self.session.flush()
