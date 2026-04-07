from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional, List, Any
from datetime import datetime
from .permission import PermissionRead


class PermissionGroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionGroupCreate(PermissionGroupBase):
    permission_ids: List[int] = []


class PermissionGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class PermissionGroupRead(PermissionGroupBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Internal links field, but we exclude it from final JSON if desired, 
    # or just use it to power the computed field.
    permission_links: List[Any] = []

    @computed_field
    @property
    def permissions(self) -> List[PermissionRead]:
        return [PermissionRead.model_validate(link.permission) 
                for link in self.permission_links if hasattr(link, "permission")]

    model_config = ConfigDict(from_attributes=True)
