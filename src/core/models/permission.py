"""
Enterprise Permission & RBAC System
====================================
Implements a scalable Role-Based Access Control (RBAC) model with support for:

- Individual permissions using a `resource:action` naming convention
- Permission groups (roles) that bundle multiple permissions
- Direct user ↔ permission assignment (overrides / fine-grained control)
- User ↔ permission group assignment (bulk role assignment)
- Explicit deny support for edge-case access revocation
- Audit fields (assigned_by, assigned_at) on every link table

Architecture:
    User ──┬──▸ UserPermissionLink ──▸ Permission
           │
           └──▸ UserPermissionGroupLink ──▸ PermissionGroup
                                                │
                                PermissionGroupPermissionLink
                                                │
                                            Permission
"""

import enum
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel

from .user import User


# ---------------------------------------------------------------------------
# Core: Permission
# ---------------------------------------------------------------------------


class PermissionCodename(str, enum.Enum):
    """Enumeration of common permission codenames to avoid hardcoding strings."""

    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"

    # Product Management
    PRODUCT_CREATE = "product:create"
    PRODUCT_READ = "product:read"
    PRODUCT_UPDATE = "product:update"
    PRODUCT_DELETE = "product:delete"
    PRODUCT_MANAGE = "product:manage"

    # Category Management
    CATEGORY_CREATE = "category:create"
    CATEGORY_READ = "category:read"
    CATEGORY_UPDATE = "category:update"
    CATEGORY_DELETE = "category:delete"
    CATEGORY_MANAGE = "category:manage"

    # Order Management
    ORDER_CREATE = "order:create"
    ORDER_READ = "order:read"
    ORDER_UPDATE = "order:update"
    ORDER_DELETE = "order:delete"
    ORDER_MANAGE = "order:manage"

    # Permission Management
    PERMISSION_MANAGE = "permission:manage"


class Permission(SQLModel, table=True):
    """
    A single, atomic permission.

    Naming convention: `resource:action`
    Examples: `product:create`, `order:read`, `user:manage`
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # Human-readable label, e.g. "Create Product"
    name: str = Field(max_length=128)
    # Machine-readable unique key, e.g. "product:create"
    codename: str = Field(unique=True, index=True, max_length=128)
    description: Optional[str] = Field(default=None, max_length=512)

    # Structured fields for programmatic filtering
    resource: str = Field(index=True, max_length=64)  # e.g. "product"
    action: str = Field(index=True)  # e.g. "create"

    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ── Relationships ──
    group_links: List["PermissionGroupPermissionLink"] = Relationship(
        back_populates="permission"
    )
    user_links: List["UserPermissionLink"] = Relationship(back_populates="permission")

    def __repr__(self) -> str:
        return f"<Permission(codename={self.codename})>"


# ---------------------------------------------------------------------------
# Core: Permission Group (Role)
# ---------------------------------------------------------------------------


class PermissionGroup(SQLModel, table=True):
    """
    A named collection of permissions – effectively a *role*.

    Examples: "Product Manager", "Order Viewer", "Super Admin"
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(unique=True, index=True, max_length=128)
    description: Optional[str] = Field(default=None, max_length=512)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ── Relationships ──
    permission_links: List["PermissionGroupPermissionLink"] = Relationship(
        back_populates="permission_group"
    )
    user_links: List["UserPermissionGroupLink"] = Relationship(
        back_populates="permission_group"
    )

    def __repr__(self) -> str:
        return f"<PermissionGroup(name={self.name})>"


# ---------------------------------------------------------------------------
# Link: PermissionGroup ↔ Permission  (many-to-many)
# ---------------------------------------------------------------------------


class PermissionGroupPermissionLink(SQLModel, table=True):
    """Associates permissions with a permission group."""

    __tablename__ = "permissiongrouppermissionlink"

    id: Optional[int] = Field(default=None, primary_key=True)
    permission_group_id: int = Field(foreign_key="permissiongroup.id", index=True)
    permission_id: int = Field(foreign_key="permission.id", index=True)

    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ── Relationships ──
    permission_group: "PermissionGroup" = Relationship(
        back_populates="permission_links"
    )
    permission: "Permission" = Relationship(back_populates="group_links")


# ---------------------------------------------------------------------------
# Link: User ↔ Permission  (direct, many-to-many)
# ---------------------------------------------------------------------------


class UserPermissionLink(SQLModel, table=True):
    """
    Directly assigns (or explicitly denies) a single permission to a user.

    Use `is_denied=True` to revoke a permission that would otherwise be
    inherited through a permission group.  Deny always wins.
    """

    __tablename__ = "userpermissionlink"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    permission_id: int = Field(foreign_key="permission.id", index=True)

    # If True, this row *removes* the permission even if a group grants it.
    is_denied: bool = Field(default=False)

    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # ID of the admin/system that made the assignment (nullable for seed data)
    assigned_by: Optional[int] = Field(default=None, foreign_key="user.id")

    # ── Relationships ──
    user: "User" = Relationship(
        back_populates="permission_links",
        sa_relationship_kwargs={"foreign_keys": "[UserPermissionLink.user_id]"},
    )
    permission: "Permission" = Relationship(back_populates="user_links")


# ---------------------------------------------------------------------------
# Link: User ↔ PermissionGroup  (many-to-many)
# ---------------------------------------------------------------------------


class UserPermissionGroupLink(SQLModel, table=True):
    """Assigns a permission group (role) to a user."""

    __tablename__ = "userpermissiongrouplink"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    permission_group_id: int = Field(foreign_key="permissiongroup.id", index=True)

    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_by: Optional[int] = Field(default=None, foreign_key="user.id")

    # ── Relationships ──
    user: "User" = Relationship(
        back_populates="permission_group_links",
        sa_relationship_kwargs={"foreign_keys": "[UserPermissionGroupLink.user_id]"},
    )
    permission_group: "PermissionGroup" = Relationship(back_populates="user_links")
