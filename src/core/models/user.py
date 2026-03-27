from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel
import enum


class UserRole(str, enum.Enum):
    """Enumeration of user roles within the system."""

    CUSTOMER = "customer"
    VENDOR = "vendor"
    ADMIN = "admin"


class User(SQLModel, table=True):
    """Core User model representing authentication and role-based access."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_active: bool = Field(default=True)

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    customer_profile: Optional["CustomerProfile"] = Relationship(back_populates="user")
    vendor_profile: Optional["VendorProfile"] = Relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User(email={self.email}, role={self.role})>"


class VendorProfile(SQLModel, table=True):
    """Storefront details for users with the VENDOR role."""

    id: Optional[int] = Field(default=None, primary_key=True)
    store_name: str = Field(index=True)
    bio: Optional[str] = Field(default=None)

    # Contact & Location
    phone: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)

    # Metadata
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    user_id: int = Field(foreign_key="user.id", unique=True)
    user: User = Relationship(back_populates="vendor_profile")

    def __repr__(self) -> str:
        return f"<VendorProfile(store_name={self.store_name})>"


class CustomerProfile(SQLModel, table=True):
    """Profile details for users with the CUSTOMER role."""

    id: Optional[int] = Field(default=None, primary_key=True)

    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    # Contact & Location
    phone: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)

    # Metadata
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user_id: int = Field(foreign_key="user.id", unique=True)
    user: User = Relationship(back_populates="customer_profile")

    def __repr__(self) -> str:
        return f"<CustomerProfile(user_id={self.user_id})>"
