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

    async def queue(self, submission_id: int) -> None:
        await self.repo.update_status(submission_id, "queued")

    async def reject(self, submission_id: int) -> None:
        await self.repo.update_status(submission_id, "rejected")

    async def publish(self, submission_id: int) -> Submission:
        submission = await self.repo.get_by_id(submission_id)

        if submission is None:
            raise ValueError("Submission not found")

        submission.status = "published"
        return submission
