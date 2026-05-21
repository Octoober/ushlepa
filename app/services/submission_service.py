from datetime import UTC, datetime, timedelta

from app.config.settings import settings
from app.database.models.submission import Submission
from app.database.repositories.submission_repository import SubmissionRepository
from app.schemas.submission_draft import SubmissionDraft


class SubmissionService:
    def __init__(self, repository: SubmissionRepository):
        self.repo = repository

    async def create_from_draft(
        self,
        user_id: int,
        is_anonymous: bool,
        draft: SubmissionDraft,
    ) -> Submission:
        return await self.repo.create(
            user_id=user_id,
            caption=draft.get("caption"),
            is_anonymous=is_anonymous,
            media_items=draft.get("media_items", []),
        )

    async def queue(self, submission_id: int) -> datetime:
        submission = await self.repo.get_by_id(submission_id)

        if submission is None:
            raise ValueError("Submission not found")

        if submission.status == "queued" and submission.publish_at is not None:
            return submission.publish_at

        interval = timedelta(minutes=settings.queue_interval_minutes)
        now = _utc_now()

        last_queued = await self.repo.get_last_queued()

        if last_queued is None or last_queued.publish_at is None:
            publish_at = now + interval
        else:
            base_time = max(now, last_queued.publish_at)
            publish_at = base_time + interval

        submission.status = "queued"
        submission.publish_at = publish_at

        return publish_at

    async def get_next_due_queued(self) -> Submission | None:
        return await self.repo.get_next_due_queued(_utc_now())

    async def get_for_publication(self, submission_id: int) -> Submission:
        submission = await self.repo.get_by_id(submission_id)

        if submission is None:
            raise ValueError("Submission not found")

        return submission

    async def mark_published(self, submission: Submission) -> None:
        submission.status = "published"
        submission.published_at = _utc_now()

    async def reject(self, submission_id: int) -> None:
        await self.repo.update_status(submission_id, "rejected")

    async def cancel(self, submission_id: int) -> None:
        submission = await self.repo.get_by_id(submission_id)

        if submission is None:
            return

        submission.status = "cancelled"
        submission.publish_at = None


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
