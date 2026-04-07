from pydantic import BaseModel
from typing import Optional


class UserPermissionAssignment(BaseModel):
    user_id: int
    permission_id: int
    is_denied: bool = False


class UserGroupAssignment(BaseModel):
    user_id: int
    group_id: int


class GroupPermissionAssignment(BaseModel):
    group_id: int
    permission_id: int
