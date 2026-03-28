from typing import Optional
from sqlmodel import select
from src.core.models.user import User, CustomerProfile, VendorProfile
from src.core.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()


class CustomerProfileRepository(BaseRepository[CustomerProfile]):
    def __init__(self, db):
        super().__init__(CustomerProfile, db)

    async def get_by_user_id(self, user_id: int) -> Optional[CustomerProfile]:
        """Fetch a customer profile by the associated user ID."""
        statement = select(CustomerProfile).where(CustomerProfile.user_id == user_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()


class VendorProfileRepository(BaseRepository[VendorProfile]):
    def __init__(self, db):
        super().__init__(VendorProfile, db)

    async def get_by_user_id(self, user_id: int) -> Optional[VendorProfile]:
        """Fetch a vendor profile by the associated user ID."""
        statement = select(VendorProfile).where(VendorProfile.user_id == user_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
