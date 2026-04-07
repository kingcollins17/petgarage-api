import traceback
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.enums import ApiTags
from src.core.schemas import GenericResponse
from src.features.permissions.schemas.permission import PermissionCreate, PermissionRead, PermissionUpdate
from src.core.repositories import get_permission_repository
from src.core.repositories.permission_repository import PermissionRepository
from src.core.models.permission import Permission, PermissionCodename
from src.services.auth_service import PermissionChecker

router = APIRouter(prefix="/permissions", tags=[ApiTags.PERMISSIONS])

@router.post("/", response_model=GenericResponse[PermissionRead], status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: PermissionCreate,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    try:
        existing = await perm_repo.get_by_codename(data.codename)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission with codename '{data.codename}' already exists."
            )
        
        new_perm = Permission(**data.model_dump())
        return {"data": await perm_repo.create(new_perm)}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create permission.")

@router.get("/", response_model=GenericResponse[List[PermissionRead]])
async def list_permissions(
    page: int = 1,
    per_page: int = 100,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    try:
        return {"data": await perm_repo.list(page=page, per_page=per_page)}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch permissions.")

@router.get("/{permission_id}", response_model=GenericResponse[PermissionRead])
async def get_permission(
    permission_id: int,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    obj = await perm_repo.get(permission_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found.")
    return {"data": obj}

@router.patch("/{permission_id}", response_model=GenericResponse[PermissionRead])
async def update_permission(
    permission_id: int,
    data: PermissionUpdate,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    obj = await perm_repo.get(permission_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found.")
        
    try:
        update_dict = data.model_dump(exclude_unset=True)
        return {"data": await perm_repo.update(obj, update_dict)}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update permission.")

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    obj = await perm_repo.get(permission_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found.")
        
    try:
        await perm_repo.delete(permission_id)
        return None
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete permission.")
