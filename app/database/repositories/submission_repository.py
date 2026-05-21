from datetime import datetime

from sqlalchemy import desc, select
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
        media_items: list[MediaItemDraft],
    ) -> Submission:
        submission = Submission(
            user_id=user_id,
            caption=caption,
            is_anonymous=is_anonymous,
            status="pending",
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

        created_submission = await self.get_by_id(submission.id)

        if created_submission is None:
            raise RuntimeError("Created submission not found")

        return created_submission

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

    async def get_last_queued(self) -> Submission | None:
        stmt = (
            select(Submission)
            .where(Submission.status == "queued")
            .where(Submission.publish_at.is_not(None))
            .order_by(desc(Submission.publish_at))
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_next_due_queued(self, now: datetime) -> Submission | None:
        stmt = (
            select(Submission)
            .options(
                selectinload(Submission.media_items),
                selectinload(Submission.user),
            )
            .where(Submission.status == "queued")
            .where(Submission.publish_at <= now)
            .order_by(Submission.publish_at)
            .limit(1)
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, submission_id: int, new_status: str) -> None:
        submission = await self.get_by_id(submission_id)

        if submission is None:
            return

        submission.status = new_status
        await self.session.flush()
