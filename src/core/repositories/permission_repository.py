from typing import Optional
from sqlmodel import select
from src.core.models.permission import (
    Permission,
    PermissionGroup,
    UserPermissionLink,
    UserPermissionGroupLink,
    PermissionGroupPermissionLink
)
from src.core.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db):
        super().__init__(Permission, db)

    async def get_by_codename(self, codename: str) -> Optional[Permission]:
        """Fetch a permission by its machine-readable codename."""
        statement = select(Permission).where(Permission.codename == codename)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
    async def get_effective_permissions_for_user(self, user_id: int) -> set[str]:
        """
        Calculates the complete set of permissions codenames for a given user.
        Accounts for:
        1. Direct grants/denials (UserPermissionLink)
        2. Group-inherited permissions (via PermissionGroup)
        3. Exclusion logic: Denials always take precedence.
        """
        # 1. Fetch direct permissions (codename + is_denied)
        direct_stmt = select(Permission.codename, UserPermissionLink.is_denied).join(
            UserPermissionLink, UserPermissionLink.permission_id == Permission.id
        ).where(UserPermissionLink.user_id == user_id)
        
        direct_results = await self.db.execute(direct_stmt)
        direct_map = {row.codename: row.is_denied for row in direct_results}
        
        # 2. Fetch group-inherited permissions
        group_stmt = select(Permission.codename).join(
            PermissionGroupPermissionLink, PermissionGroupPermissionLink.permission_id == Permission.id
        ).join(
            UserPermissionGroupLink, UserPermissionGroupLink.permission_group_id == PermissionGroupPermissionLink.permission_group_id
        ).where(UserPermissionGroupLink.user_id == user_id)
        
        group_results = await self.db.execute(group_stmt)
        group_permissions = {row.codename for row in group_results}
        
        # 3. Apply logic: Add group permissions unless directly denied
        effective = {p for p in group_permissions if direct_map.get(p) is not True}
        
        # 4. Add direct grants (is_denied=False)
        effective.update({p for p, is_denied in direct_map.items() if not is_denied})
        
        return effective

    async def assign_to_user(self, user_id: int, permission_id: int, assigned_by_id: int, is_denied: bool = False) -> UserPermissionLink:
        """Directly assigns a permission to a user."""
        link = UserPermissionLink(user_id=user_id, permission_id=permission_id, assigned_by=assigned_by_id, is_denied=is_denied)
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def remove_from_user(self, user_id: int, permission_id: int) -> bool:
        """Removes a direct permission assignment from a user."""
        statement = select(UserPermissionLink).where(UserPermissionLink.user_id == user_id, UserPermissionLink.permission_id == permission_id)
        result = await self.db.execute(statement)
        link = result.scalar_one_or_none()
        if link:
            await self.db.delete(link)
            await self.db.commit()
            return True
        return False


class PermissionGroupRepository(BaseRepository[PermissionGroup]):
    def __init__(self, db):
        super().__init__(PermissionGroup, db)

    async def get_by_name(self, name: str) -> Optional[PermissionGroup]:
        """Fetch a permission group by its name."""
        statement = select(PermissionGroup).where(PermissionGroup.name == name)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def assign_to_user(self, user_id: int, group_id: int, assigned_by_id: int) -> UserPermissionGroupLink:
        """Assigns a permission group to a user."""
        link = UserPermissionGroupLink(user_id=user_id, permission_group_id=group_id, assigned_by=assigned_by_id)
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def remove_from_user(self, user_id: int, group_id: int) -> bool:
        """Removes a group assignment from a user."""
        statement = select(UserPermissionGroupLink).where(UserPermissionGroupLink.user_id == user_id, UserPermissionGroupLink.permission_group_id == group_id)
        result = await self.db.execute(statement)
        link = result.scalar_one_or_none()
        if link:
            await self.db.delete(link)
            await self.db.commit()
            return True
        return False

    async def add_permission(self, group_id: int, permission_id: int) -> PermissionGroupPermissionLink:
        """Adds a single permission to a group."""
        link = PermissionGroupPermissionLink(permission_group_id=group_id, permission_id=permission_id)
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def remove_permission(self, group_id: int, permission_id: int) -> bool:
        """Removes a single permission from a group."""
        statement = select(PermissionGroupPermissionLink).where(PermissionGroupPermissionLink.permission_group_id == group_id, PermissionGroupPermissionLink.permission_id == permission_id)
        result = await self.db.execute(statement)
        link = result.scalar_one_or_none()
        if link:
            await self.db.delete(link)
            await self.db.commit()
            return True
        return False
