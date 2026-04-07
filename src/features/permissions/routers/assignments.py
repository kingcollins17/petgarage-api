import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.enums import ApiTags
from src.core.schemas import GenericResponse
from src.core.models.user import User
from src.core.models.permission import PermissionCodename
from src.features.permissions.schemas.assignment import UserPermissionAssignment, UserGroupAssignment
from src.core.repositories import get_permission_repository, get_permission_group_repository
from src.core.repositories.permission_repository import PermissionRepository, PermissionGroupRepository
from src.services.auth_service import get_current_admin, PermissionChecker

router = APIRouter(prefix="/assignments", tags=[ApiTags.PERMISSIONS])

@router.post("/user-permissions", response_model=GenericResponse[None])
async def assign_permission_to_user(
    data: UserPermissionAssignment,
    current_admin: User = Depends(get_current_admin),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    """Directly assigns a permission to a user (or explicitly denies it)."""
    try:
        if current_admin.id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin session.")
            
        await perm_repo.assign_to_user(
            user_id=data.user_id,
            permission_id=data.permission_id,
            assigned_by_id=current_admin.id,
            is_denied=data.is_denied
        )
        return {"message": "Permission assigned successfully."}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign permission.")

@router.delete("/user-permissions/{user_id}/{permission_id}", response_model=GenericResponse[None])
async def remove_permission_from_user(
    user_id: int,
    permission_id: int,
    _: User = Depends(get_current_admin),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    """Removes a direct permission assignment from a user."""
    try:
        success = await perm_repo.remove_from_user(user_id, permission_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")
        return {"message": "Permission removed successfully."}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove permission.")

@router.post("/user-groups", response_model=GenericResponse[None])
async def assign_group_to_user(
    data: UserGroupAssignment,
    current_admin: User = Depends(get_current_admin),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository)
):
    """Assigns a permission group (role) to a user."""
    try:
        if current_admin.id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin session.")
            
        await pg_repo.assign_to_user(
            user_id=data.user_id,
            group_id=data.group_id,
            assigned_by_id=current_admin.id
        )
        return {"message": "Group assigned successfully."}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign group.")

@router.delete("/user-groups/{user_id}/{group_id}", response_model=GenericResponse[None])
async def remove_group_from_user(
    user_id: int,
    group_id: int,
    _: User = Depends(get_current_admin),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository)
):
    """Removes a group assignment from a user."""
    try:
        success = await pg_repo.remove_from_user(user_id, group_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found.")
        return {"message": "Group removed successfully."}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove group.")
