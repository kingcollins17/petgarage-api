import traceback
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from src.features.accounts.schemas.auth import (
    UserRead, UserUpdate,
    CustomerProfileRead, CustomerProfileUpdate,
    VendorProfileRead, VendorProfileUpdate
)
from src.core.models.user import User, UserRole, CustomerProfile, VendorProfile
from src.core.repositories.user_repository import (
    UserRepository, 
    CustomerProfileRepository, 
    VendorProfileRepository
)
from src.core.repositories import (
    get_user_repository,
    get_customer_profile_repository,
    get_vendor_profile_repository
)
from src.services.auth_service import (
    get_current_user,
    get_current_customer,
    get_current_vendor
)

router = APIRouter(prefix="/accounts", tags=["Account Management"])


@router.get("/me", response_model=UserRead)
async def get_my_account(current_user: User = Depends(get_current_user)):
    """Fetches identifying information about the currently logged-in user."""
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_my_account(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Updates the currently authenticated user's account details."""
    try:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return current_user

        if "email" in data and data["email"] != current_user.email:
            existing = await user_repo.get_by_email(data["email"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use by another account."
                )

        return await user_repo.update(current_user, data)
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account update failed due to an internal server error."
        )


@router.get("/me/profile", response_model=Union[CustomerProfileRead, VendorProfileRead])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    customer_repo: CustomerProfileRepository = Depends(get_customer_profile_repository),
    vendor_repo: VendorProfileRepository = Depends(get_vendor_profile_repository)
):
    """Returns the profile associated with the current user's role."""
    try:
        # Check user.id to satisfy type checker
        if current_user.id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")

        if current_user.role == UserRole.CUSTOMER:
            profile = await customer_repo.get_by_user_id(current_user.id)
            if not profile:
                raise HTTPException(status_code=404, detail="Customer profile not found.")
            return profile
        elif current_user.role == UserRole.VENDOR:
            profile = await vendor_repo.get_by_user_id(current_user.id)
            if not profile:
                raise HTTPException(status_code=404, detail="Vendor profile not found.")
            return profile
        else:
            raise HTTPException(status_code=400, detail="User role does not have a managed profile.")
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch profile.")


@router.patch("/me/customer-profile", response_model=CustomerProfileRead)
async def update_customer_profile(
    update_data: CustomerProfileUpdate,
    current_user: User = Depends(get_current_customer),
    customer_repo: CustomerProfileRepository = Depends(get_customer_profile_repository)
):
    """Updates (or creates) the customer profile for the current user."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")

        profile = await customer_repo.get_by_user_id(current_user.id)
        data = update_data.model_dump(exclude_unset=True)
        
        if profile:
            return await customer_repo.update(profile, data)
        else:
            new_profile = CustomerProfile(**data, user_id=current_user.id)
            return await customer_repo.create(new_profile)
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update customer profile.")


@router.patch("/me/vendor-profile", response_model=VendorProfileRead)
async def update_vendor_profile(
    update_data: VendorProfileUpdate,
    current_user: User = Depends(get_current_vendor),
    vendor_repo: VendorProfileRepository = Depends(get_vendor_profile_repository)
):
    """Updates (or creates) the vendor profile for the current user."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session.")

        profile = await vendor_repo.get_by_user_id(current_user.id)
        data = update_data.model_dump(exclude_unset=True)
        
        if profile:
            return await vendor_repo.update(profile, data)
        else:
            new_profile = VendorProfile(**data, user_id=current_user.id)
            return await vendor_repo.create(new_profile)
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update vendor profile.")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Deactivates and deletes the current user's account."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        await user_repo.delete(current_user.id)
        return None
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete account. Please contact support."
        )
