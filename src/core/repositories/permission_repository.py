from typing import Optional
from sqlmodel import select
from src.core.models.permission import Permission, PermissionGroup
from src.core.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, db):
        super().__init__(Permission, db)

    async def get_by_codename(self, codename: str) -> Optional[Permission]:
        """Fetch a permission by its machine-readable codename."""
        statement = select(Permission).where(Permission.codename == codename)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()


class PermissionGroupRepository(BaseRepository[PermissionGroup]):
    def __init__(self, db):
        super().__init__(PermissionGroup, db)

    async def get_by_name(self, name: str) -> Optional[PermissionGroup]:
        """Fetch a permission group by its name."""
        statement = select(PermissionGroup).where(PermissionGroup.name == name)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
