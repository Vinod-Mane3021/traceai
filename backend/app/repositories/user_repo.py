import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import CreateUser, UpdateUser
from app.models.core import User
from sqlalchemy import select, insert, update

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
            )
            .returning(User)
        )
        await self.session.commit()
        created_user = result.scalar_one()
        log.info("user_created", message="Successfully created new user record", user_id=created_user.id)
        return created_user

    async def get_user_by_github_id(self, github_id: int) -> User | None:
        """
        get user by github id
        """
        log = logger.bind(method="get_user_by_github_id", github_id=github_id)
        log.info("fetching_user", message="Fetching user by GitHub ID from the database")

        result = await self.session.execute(
            select(User)
            .where(User.github_id == github_id)
        )
        user = result.scalars().first()

        if user:
            log.info("user_found", message="User found in the database", user_id=user.id)
        else:
            log.info("user_not_found", message="No user found with the given GitHub ID")

        return user
    
    async def update_user(self, user_id: int, user_data: UpdateUser) -> User:
        """
        Update user information based on provided data.
        """
        log = logger.bind(method="update_user", user_id=user_id)
        log.info("updating_user_info", message="Updating user information", update_fields=user_data.dict(exclude_unset=True))

        # Build the update statement dynamically based on which fields are provided
        update_values = {k: v for k, v in user_data.dict(exclude_unset=True).items()}

        if not update_values:
            log.info("no_update_fields", message="No fields provided for update, skipping database operation")
            return await self.session.get(User, user_id)

        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_values)
        )
        await self.session.commit()
        log.info("user_info_updated", message="Successfully updated user information")

        return await self.session.get(User, user_id)
        