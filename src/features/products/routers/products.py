import traceback
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.core.enums import ApiTags
from src.core.schemas import GenericResponse
from src.features.products.schemas.product import ProductCreate, ProductUpdate, ProductRead
from src.core.repositories import get_product_repository, get_category_repository
from src.core.repositories.product_repository import ProductRepository, CategoryRepository
from src.core.models.product import Product
from src.services.auth_service import get_current_user, PermissionChecker
from src.core.models.user import User, UserRole
from src.core.models.permission import PermissionCodename

router = APIRouter(prefix="/products", tags=[ApiTags.PRODUCTS])

@router.post("/", response_model=GenericResponse[ProductRead], status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(PermissionChecker([PermissionCodename.PRODUCT_CREATE])),
    product_repo: ProductRepository = Depends(get_product_repository),
    category_repo: CategoryRepository = Depends(get_category_repository)
):
    if not current_user.vendor_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vendor profile not found.")
        
    try:
        product_data = data.model_dump(exclude={"category_ids"})
        new_record = Product(**product_data, vendor_id=current_user.vendor_profile.id)
        
        if data.category_ids:
            for cat_id in data.category_ids:
                cat = await category_repo.get(cat_id)
                if cat:
                    new_record.categories.append(cat)
                    
        return {"data": await product_repo.create(new_record)}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create product.")

@router.get("/", response_model=GenericResponse[List[ProductRead]])
async def list_products(
    page: int = 1,
    per_page: int = 100,
    product_repo: ProductRepository = Depends(get_product_repository)
):
    try:
        # Load products eagerly with their categories
        offset = (page - 1) * per_page
        statement = select(Product).options(selectinload(Product.categories)).offset(offset).limit(per_page)
        results = await product_repo.db.execute(statement)
        return {"data": results.scalars().all()}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch products.")

@router.get("/{product_id}", response_model=GenericResponse[ProductRead])
async def get_product(
    product_id: int,
    product_repo: ProductRepository = Depends(get_product_repository)
):
    statement = select(Product).where(Product.id == product_id).options(selectinload(Product.categories))
    results = await product_repo.db.execute(statement)
    obj = results.scalars().first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return {"data": obj}

@router.patch("/{product_id}", response_model=GenericResponse[ProductRead])
async def update_product(
    product_id: int,
    data: ProductUpdate,
    current_user: User = Depends(PermissionChecker([PermissionCodename.PRODUCT_UPDATE])),
    product_repo: ProductRepository = Depends(get_product_repository),
    category_repo: CategoryRepository = Depends(get_category_repository)
):
    statement = select(Product).where(Product.id == product_id).options(selectinload(Product.categories))
    results = await product_repo.db.execute(statement)
    obj = results.scalars().first()
    
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        
    if current_user.role != UserRole.ADMIN and (current_user.role != UserRole.VENDOR or not current_user.vendor_profile or obj.vendor_id != current_user.vendor_profile.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this product.")
        
    try:
        update_data = data.model_dump(exclude_unset=True)
        category_ids = update_data.pop("category_ids", None)
        
        # update basic fields
        for field, value in update_data.items():
            setattr(obj, field, value)
            
        # update categories if provided
        if category_ids is not None:
            obj.categories.clear() # remove existing
            for cat_id in category_ids:
                cat = await category_repo.get(cat_id)
                if cat:
                    obj.categories.append(cat)
                    
        product_repo.db.add(obj)
        await product_repo.db.commit()
        await product_repo.db.refresh(obj) # to get updated IDs if needed
        return {"data": obj}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update product.")

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(PermissionChecker([PermissionCodename.PRODUCT_DELETE])),
    product_repo: ProductRepository = Depends(get_product_repository)
):
    obj = await product_repo.get(product_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
        
    if current_user.role != UserRole.ADMIN and (current_user.role != UserRole.VENDOR or not current_user.vendor_profile or obj.vendor_id != current_user.vendor_profile.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this product.")
        
    try:
        await product_repo.delete(product_id)
        return None
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete product.")
