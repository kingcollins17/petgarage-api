from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PermissionBase(BaseModel):
    name: str
    codename: str
    description: Optional[str] = None
    resource: str
    action: str


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionRead(PermissionBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
