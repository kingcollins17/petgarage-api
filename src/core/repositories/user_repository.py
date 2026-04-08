from typing import Optional, List
from sqlmodel import select, col
from src.core.models.user import User, CustomerProfile, VendorProfile, UserRole
from src.core.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their email address."""
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def list(
        self,
        page: int = 1,
        per_page: int = 100,
        role: Optional[str] = None,
        active: Optional[bool] = None,
        verified: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Fetch a filtered and paginated list of users."""
        offset = (page - 1) * per_page
        
        statement = select(User)

        # Filters
        if role:
            statement = statement.where(User.role == role)
        if active is not None:
            statement = statement.where(User.active == active)
        if verified is not None:
            statement = statement.where(User.verified == verified)
        if search:
            search_filter = f"%{search}%"
            statement = statement.where(
                (col(User.email).ilike(search_filter)) | 
                (col(User.full_name).ilike(search_filter))
            )

        statement = statement.offset(offset).limit(per_page).order_by(col(User.id).desc())
        result = await self.db.execute(statement)
        return result.scalars().all()


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
