import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import CreateUser
from app.models.core import User
from sqlalchemy import select, insert

logger = structlog.get_logger(__name__)

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user_if_not_exists(self, user_data: CreateUser) -> User:
        """
        create user if not exists else just return
        """
        log = logger.bind(method="create_user_if_not_exists", github_id=user_data.github_id)
        log.info("checking_user_existence", message="Checking if user already exists in the database", username=user_data.username)

        # find the user
        existing_user_response = await self.session.execute(
            select(User)
            .where(User.github_id == user_data.github_id)
        )
        existing_user = existing_user_response.scalars().first()

        if existing_user:
            log.info("user_already_exists", message="User already exists, returning existing user", user_id=existing_user.id)
            return existing_user
        
        # create the user
        log.info("creating_new_user", message="User not found, creating a new user record", username=user_data.username)
        
        result = await self.session.execute(
            insert(User)
            .values(
                username=user_data.username,
                avatar_url=user_data.avatar_url,
                github_id=user_data.github_id,
                installation_id=user_data.installation_id
            )
            .returning(User)
        )
        await self.session.commit()
        created_user = result.scalar_one()
        log.info("user_created", message="Successfully created new user record", user_id=created_user.id)
        return created_user
