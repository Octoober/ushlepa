from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.submission_repository import SubmissionRepository
from app.database.repositories.user_repository import UserRepository
from app.services.submission_service import SubmissionService
from app.services.user_service import UserService


class ServiceContainer:
    def __init__(self, session: AsyncSession):
        user_repo = UserRepository(session)
        submission_repo = SubmissionRepository(session)

        self.users = UserService(user_repo)
        self.submissions = SubmissionService(submission_repo)
