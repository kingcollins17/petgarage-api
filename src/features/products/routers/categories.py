import traceback
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.enums import ApiTags
from src.core.schemas import GenericResponse
from src.features.products.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from src.core.repositories import get_category_repository
from src.core.repositories.product_repository import CategoryRepository
from src.core.models.product import Category
from src.services.auth_service import get_current_user, PermissionChecker
from src.core.models.user import User, UserRole
from src.core.models.permission import PermissionCodename

router = APIRouter(prefix="/categories", tags=[ApiTags.CATEGORIES])

@router.post("/", response_model=GenericResponse[CategoryRead], status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(PermissionChecker([PermissionCodename.CATEGORY_CREATE])),
    repo: CategoryRepository = Depends(get_category_repository)
):
    try:
        new_record = Category(**data.model_dump())
        return {"data": await repo.create(new_record)}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create category.")

@router.get("/", response_model=GenericResponse[List[CategoryRead]])
async def list_categories(
    page: int = 1,
    per_page: int = 100,
    repo: CategoryRepository = Depends(get_category_repository)
):
    try:
        return {"data": await repo.list(page=page, per_page=per_page)}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch categories.")

@router.get("/{category_id}", response_model=GenericResponse[CategoryRead])
async def get_category(
    category_id: int,
    repo: CategoryRepository = Depends(get_category_repository)
):
    obj = await repo.get(category_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
    return {"data": obj}

@router.patch("/{category_id}", response_model=GenericResponse[CategoryRead])
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: User = Depends(PermissionChecker([PermissionCodename.CATEGORY_UPDATE])),
    repo: CategoryRepository = Depends(get_category_repository)
):
    obj = await repo.get(category_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        
    try:
        return {"data": await repo.update(obj, data.model_dump(exclude_unset=True))}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update category.")

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(PermissionChecker([PermissionCodename.CATEGORY_DELETE])),
    repo: CategoryRepository = Depends(get_category_repository)
):
    try:
        obj = await repo.get(category_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found.")
        await repo.delete(category_id)
        return None
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete category.")
