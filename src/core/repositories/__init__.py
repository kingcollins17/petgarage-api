from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_connection import get_db
from .base import BaseRepository
from .user_repository import (
    UserRepository,
    CustomerProfileRepository,
    VendorProfileRepository,
)
from .product_repository import ProductRepository, PetDetailRepository, CategoryRepository
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


def get_customer_profile_repository(db: AsyncSession = Depends(get_db)):
    return CustomerProfileRepository(db=db)


def get_vendor_profile_repository(db: AsyncSession = Depends(get_db)):
    return VendorProfileRepository(db=db)


def get_permission_repository(db: AsyncSession = Depends(get_db)):
    return PermissionRepository(db=db)


def get_product_repository(db: AsyncSession = Depends(get_db)):
    return ProductRepository(db=db)


def get_category_repository(db: AsyncSession = Depends(get_db)):
    return CategoryRepository(db=db)


def get_permission_group_repository(db: AsyncSession = Depends(get_db)):
    return PermissionGroupRepository(db=db)
