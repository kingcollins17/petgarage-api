import traceback
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.core.enums import ApiTags
from src.core.schemas import GenericResponse
from src.features.permissions.schemas.permission_group import PermissionGroupCreate, PermissionGroupRead, PermissionGroupUpdate
from src.core.repositories import get_permission_repository, get_permission_group_repository
from src.core.repositories.permission_repository import PermissionRepository, PermissionGroupRepository
from src.core.models.permission import PermissionGroup, PermissionGroupPermissionLink, PermissionCodename
from src.services.auth_service import PermissionChecker

router = APIRouter(prefix="/permission-groups", tags=[ApiTags.PERMISSION_GROUPS])

@router.post("/", response_model=GenericResponse[PermissionGroupRead], status_code=status.HTTP_201_CREATED)
async def create_permission_group(
    data: PermissionGroupCreate,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    try:
        existing = await pg_repo.get_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Permission group with name '{data.name}' already exists."
            )
        
        pg_data = data.model_dump(exclude={"permission_ids"})
        new_record = PermissionGroup(**pg_data)
        
        if data.permission_ids:
            for perm_id in data.permission_ids:
                perm = await perm_repo.get(perm_id)
                if perm:
                    # Link table PermissionGroupPermissionLink
                    link = PermissionGroupPermissionLink(permission_group=new_record, permission=perm)
                    new_record.permission_links.append(link)
                    
        return {"data": await pg_repo.create(new_record)}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create permission group.")

@router.get("/", response_model=GenericResponse[List[PermissionGroupRead]])
async def list_permission_groups(
    page: int = 1,
    per_page: int = 100,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository)
):
    try:
        # Load groups eagerly with their permissions
        offset = (page - 1) * per_page
        # We need to reach Permission via PermissionGroupPermissionLink
        statement = select(PermissionGroup).options(
            selectinload(PermissionGroup.permission_links).selectinload(PermissionGroupPermissionLink.permission)
        ).offset(offset).limit(per_page)
        results = await pg_repo.db.execute(statement)
        # Note: PermissionGroupRead has a List[PermissionRead] field. 
        # The model has permission_links. We need to handle the transformation or ensure the schema matches.
        # Actually PermissionGroup model doesn't have a direct 'permissions' relationship in the view I saw.
        # Let's double check PermissionGroup model in src/core/models/permission.py
        return {"data": results.scalars().all()}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch permission groups.")

@router.get("/{group_id}", response_model=GenericResponse[PermissionGroupRead])
async def get_permission_group(
    group_id: int,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository)
):
    statement = select(PermissionGroup).where(PermissionGroup.id == group_id).options(
        selectinload(PermissionGroup.permission_links).selectinload(PermissionGroupPermissionLink.permission)
    )
    results = await pg_repo.db.execute(statement)
    obj = results.scalars().first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission group not found.")
    return {"data": obj}

@router.patch("/{group_id}", response_model=GenericResponse[PermissionGroupRead])
async def update_permission_group(
    group_id: int,
    data: PermissionGroupUpdate,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository),
    perm_repo: PermissionRepository = Depends(get_permission_repository)
):
    statement = select(PermissionGroup).where(PermissionGroup.id == group_id).options(
        selectinload(PermissionGroup.permission_links)
    )
    results = await pg_repo.db.execute(statement)
    obj = results.scalars().first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission group not found.")
        
    try:
        update_data = data.model_dump(exclude_unset=True)
        permission_ids = update_data.pop("permission_ids", None)
        
        # update basic fields
        for field, value in update_data.items():
            setattr(obj, field, value)
            
        # update permissions if provided
        if permission_ids is not None:
            # Clear existing links
            # We can't just clear 'permissions' if it's via links, but we can clear links
            obj.permission_links.clear()
            for perm_id in permission_ids:
                perm = await perm_repo.get(perm_id)
                if perm:
                    link = PermissionGroupPermissionLink(permission_group=obj, permission=perm)
                    obj.permission_links.append(link)
                    
        pg_repo.db.add(obj)
        await pg_repo.db.commit()
        await pg_repo.db.refresh(obj)
        
        # Reload with nested permissions for response
        statement_reload = select(PermissionGroup).where(PermissionGroup.id == group_id).options(
            selectinload(PermissionGroup.permission_links).selectinload(PermissionGroupPermissionLink.permission)
        )
        results_reload = await pg_repo.db.execute(statement_reload)
        obj = results_reload.scalars().first()
        
        return {"data": obj}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update permission group.")

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission_group(
    group_id: int,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository)
):
    obj = await pg_repo.get(group_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission group not found.")
        
    try:
        await pg_repo.delete(group_id)
        return None
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete permission group.")

@router.post("/{group_id}/permissions/{permission_id}", response_model=GenericResponse[None])
async def add_permission_to_group(
    group_id: int,
    permission_id: int,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository)
):
    """Adds a single permission to a group."""
    try:
        await pg_repo.add_permission(group_id, permission_id)
        return {"message": "Permission added to group successfully."}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add permission to group.")

@router.delete("/{group_id}/permissions/{permission_id}", response_model=GenericResponse[None])
async def remove_permission_from_group(
    group_id: int,
    permission_id: int,
    _: None = Depends(PermissionChecker([PermissionCodename.PERMISSION_MANAGE])),
    pg_repo: PermissionGroupRepository = Depends(get_permission_group_repository)
):
    """Removes a single permission from a group."""
    try:
        success = await pg_repo.remove_permission(group_id, permission_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found in group.")
        return {"message": "Permission removed from group successfully."}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to remove permission from group.")
