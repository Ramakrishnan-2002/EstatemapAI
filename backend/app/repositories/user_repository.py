from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Data access repository for User entity operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch user by primary key ID."""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by email (case-insensitive search)."""
        stmt = select(User).where(User.email == email.strip().lower())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        hashed_password: str,
        full_name: str | None = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        """Insert a new user record into the database."""
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update(self, user: User, update_data: dict[str, Any]) -> User:
        """Update fields on an existing user instance."""
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        await self.session.flush()
        await self.session.refresh(user)
        return user
