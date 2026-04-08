import traceback
from typing import Union, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from src.core.enums import ApiTags
from src.core.schemas import GenericResponse
from src.features.accounts.schemas.auth import (
    UserRead, UserUpdate, UserStatusUpdate, OTPVerify,
    CustomerProfileRead, CustomerProfileUpdate,
    VendorProfileRead, VendorProfileUpdate
)
from src.core.schemas.generic import PaginatedResponse, PaginationMeta

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
    get_current_vendor,
    get_current_admin,
    AuthService,
    get_auth_service
)

router = APIRouter(prefix="/accounts", tags=[ApiTags.ACCOUNT_MANAGEMENT])


@router.get("/me", response_model=GenericResponse[UserRead])
async def get_my_account(current_user: User = Depends(get_current_user)):
    """Fetches identifying information about the currently logged-in user."""
    return {"data": current_user}


@router.patch("/me", response_model=GenericResponse[UserRead])
async def update_my_account(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Updates the currently authenticated user's account details."""
    try:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return {"data": current_user}

        if "email" in data and data["email"] != current_user.email:
            existing = await user_repo.get_by_email(data["email"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use by another account."
                )

        return {"data": await user_repo.update(current_user, data)}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account update failed due to an internal server error."
        )


@router.get("/me/profile", response_model=GenericResponse[Union[CustomerProfileRead, VendorProfileRead]])
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
            return {"data": profile}
        elif current_user.role == UserRole.VENDOR:
            profile = await vendor_repo.get_by_user_id(current_user.id)
            if not profile:
                raise HTTPException(status_code=404, detail="Vendor profile not found.")
            return {"data": profile}
        else:
            raise HTTPException(status_code=400, detail="User role does not have a managed profile.")
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch profile.")


@router.patch("/me/customer-profile", response_model=GenericResponse[CustomerProfileRead])
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
            return {"data": await customer_repo.update(profile, data)}
        else:
            new_profile = CustomerProfile(**data, user_id=current_user.id)
            return {"data": await customer_repo.create(new_profile)}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update customer profile.")


@router.patch("/me/vendor-profile", response_model=GenericResponse[VendorProfileRead])
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
            return {"data": await vendor_repo.update(profile, data)}
        else:
            new_profile = VendorProfile(**data, user_id=current_user.id)
            return {"data": await vendor_repo.create(new_profile)}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update vendor profile.")


@router.post("/verify", response_model=GenericResponse[None])
async def verify_my_account(
    request: OTPVerify,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verifies the currently logged-in user's account using an OTP."""
    try:
        success = await auth_service.verify_account(request.email, request.otp)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification failed. Invalid or expired OTP."
            )
        return GenericResponse(message="Account verified successfully")
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed due to a server error."
        )


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
# Admin Endpoints

@router.get("/", response_model=PaginatedResponse[List[UserRead]], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def list_users(
    page: int = 1,
    per_page: int = 100,
    role: Optional[UserRole] = None,
    active: Optional[bool] = None,
    verified: Optional[bool] = None,
    search: Optional[str] = None,
    admin_user: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Lists all users in the system with pagination and filters (Admin only)."""
    try:
        users = await user_repo.list(
            page=page,
            per_page=per_page,
            role=role,
            active=active,
            verified=verified,
            search=search
        )
        return {
            "data": users,
            "metadata": {
                "total": len(users),
                "page": page,
                "per_page": per_page
            }
        }
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch users.")


@router.patch("/{user_id}/status", response_model=GenericResponse[UserRead], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    admin_user: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Updates a user's active/verified status (Admin only)."""
    try:
        user = await user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        data = status_data.model_dump(exclude_unset=True)
        updated_user = await user_repo.update(user, data)
        return {"data": updated_user}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update user status.")


@router.post("/{user_id}/deactivate", response_model=GenericResponse[UserRead], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Deactivates a user account (Admin only)."""
    try:
        user = await user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        updated_user = await user_repo.update(user, {"active": False})
        return {"data": updated_user}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to deactivate user.")


@router.post("/{user_id}/verify", response_model=GenericResponse[UserRead], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def verify_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Manually verifies a user's email (Admin only)."""
    try:
        user = await user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        updated_user = await user_repo.update(user, {"verified": True})
        return {"data": updated_user}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to verify user.")


@router.get("/{user_id}", response_model=GenericResponse[UserRead], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def get_user_detail(
    user_id: int,
    admin_user: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Fetches details for any user (Admin only)."""
    try:
        user = await user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        return {"data": user}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch user.")


@router.patch("/{user_id}", response_model=GenericResponse[UserRead], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def admin_update_user(
    user_id: int,
    update_data: UserUpdate,
    admin_user: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Updates any user's profile details (Admin only)."""
    try:
        user = await user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        data = update_data.model_dump(exclude_unset=True)
        updated_user = await user_repo.update(user, data)
        return {"data": updated_user}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update user.")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def admin_delete_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Permanently deletes any user account (Admin only)."""
    try:
        user = await user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")
        
        await user_repo.delete(user_id)
        return None
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to delete user account.")


@router.patch("/{user_id}/customer-profile", response_model=GenericResponse[CustomerProfileRead], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def admin_update_customer_profile(
    user_id: int,
    update_data: CustomerProfileUpdate,
    admin_user: User = Depends(get_current_admin),
    customer_repo: CustomerProfileRepository = Depends(get_customer_profile_repository)
):
    """Updates (or creates) any user's customer profile (Admin only)."""
    try:
        profile = await customer_repo.get_by_user_id(user_id)
        data = update_data.model_dump(exclude_unset=True)
        
        if profile:
            return {"data": await customer_repo.update(profile, data)}
        else:
            new_profile = CustomerProfile(**data, user_id=user_id)
            return {"data": await customer_repo.create(new_profile)}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update customer profile.")


@router.patch("/{user_id}/vendor-profile", response_model=GenericResponse[VendorProfileRead], tags=[ApiTags.ADMIN_ACCOUNT_MANAGEMENT])
async def admin_update_vendor_profile(
    user_id: int,
    update_data: VendorProfileUpdate,
    admin_user: User = Depends(get_current_admin),
    vendor_repo: VendorProfileRepository = Depends(get_vendor_profile_repository)
):
    """Updates (or creates) any user's vendor profile (Admin only)."""
    try:
        profile = await vendor_repo.get_by_user_id(user_id)
        data = update_data.model_dump(exclude_unset=True)
        
        if profile:
            return {"data": await vendor_repo.update(profile, data)}
        else:
            new_profile = VendorProfile(**data, user_id=user_id)
            return {"data": await vendor_repo.create(new_profile)}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to update vendor profile.")
