from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_connection import get_db
from .base import BaseRepository
from .user_repository import (
    UserRepository,
    CustomerProfileRepository,
    VendorProfileRepository,
)
from .product_repository import ProductRepository, PetDetailRepository
from .order_repository import (
    OrderRepository,
    OrderItemRepository,
    PaymentRepository,
    RefundRepository,
)
from .permission_repository import (
    PermissionRepository,
    PermissionGroupRepository,
)


def get_user_repository(db: AsyncSession = Depends(get_db)):
    return UserRepository(db=db)
