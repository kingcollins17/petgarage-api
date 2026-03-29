import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.features.accounts.schemas.auth import (
    UserCreate,
    UserRead,
    UserLogin,
    TokenResponse,
    OTPRequest,
    OTPVerify,
    PasswordChange,
    PasswordReset,
)
from src.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["Accounts"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)
):
    """Registers a new user."""
    try:
        # Check if user already exists
        existing_user = await auth_service.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        return await auth_service.signup_user(user_data.model_dump())
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating your account. Please try again later.",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Authenticates a user and returns a token (Supports form data for Swagger UI)."""
    try:
        result = await auth_service.login(form_data.username, form_data.password)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return result
    except HTTPException:
        traceback.print_exc()
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed due to a server error.",
        )


@router.post("/send-otp")
async def send_otp(
    request: OTPRequest, auth_service: AuthService = Depends(get_auth_service)
):
    """Sends an OTP to the user's email."""
    try:
        success = await auth_service.send_otp(request.email)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to send OTP"
            )
        return {"message": "OTP sent successfully"}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process OTP request at this time.",
        )


@router.post("/verify-otp")
async def verify_otp(
    request: OTPVerify, auth_service: AuthService = Depends(get_auth_service)
):
    """Verifies the provided OTP."""
    try:
        success = await auth_service.verify_otp(request.email, request.otp)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP"
            )
        return {"message": "OTP verified successfully"}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OTP verification failed due to a server error.",
        )


@router.post("/change-password")
async def change_password(
    request: PasswordChange,
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Changes the password for the current user."""
    try:
        success = await auth_service.change_password(
            user_id, request.old_password, request.new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
            )
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed due to a server error.",
        )


@router.post("/reset-password")
async def reset_password(
    request: PasswordReset, auth_service: AuthService = Depends(get_auth_service)
):
    """Resets the user's password using an OTP."""
    try:
        success = await auth_service.reset_password(
            request.email, request.new_password, request.otp
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password. Please verify OTP and email.",
            )
        return {"message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed due to a server error.",
        )
