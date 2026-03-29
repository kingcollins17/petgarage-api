from typing import Any, Dict, List, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db_connection import get_db
from src.core.models.permission import (
    Permission,
    PermissionCodename,
)
from src.core.models.user import User, UserRole
from src.core.repositories import get_permission_repository, get_user_repository
from src.core.repositories.permission_repository import PermissionRepository
from src.core.repositories.user_repository import UserRepository
from src.core.security import Security, get_security
from src.core.config import config


class AuthService:
    """
    Service class for handling authentication-related business logic.
    """

    def __init__(self, user_repository: UserRepository, security: Security):
        self.user_repo = user_repository
        self.security = security

    async def signup_user(self, user_data: Dict[str, Any]) -> User:
        """
        Registers a new user in the system.
        """
        # Hash the password before saving
        password = user_data.pop("password")
        hashed_password = self.security.hash_password(password)
        
        user = User(**user_data, hashed_password=hashed_password)
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticates a user and returns a JWT token if successful.
        """
        user = await self.user_repo.get_by_email(email)
        if not user or not user.hashed_password:
            return None
            
        if not self.security.verify_password(password, user.hashed_password):
            return None
            
        # Create access token
        token_data = {"sub": user.email, "role": user.role}
        access_token = self.security.create_jwt_token(data=token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    async def send_otp(self, email: str) -> bool:
        """
        Sends an OTP to the user's email (Mock implementation).
        """
        print(f"MOCK: Sending OTP to {email}")
        return True

    async def verify_otp(self, email: str, otp: str) -> bool:
        """
        Verifies the OTP provided by the user (Mock implementation).
        """
        print(f"MOCK: Verifying OTP {otp} for {email}")
        return otp == "123456" 

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Changes the user's password after verifying the old password.
        """
        user = await self.user_repo.get(user_id)
        if not user or not user.hashed_password:
            return False
            
        if not self.security.verify_password(old_password, user.hashed_password):
            return False
            
        new_hashed_password = self.security.hash_password(new_password)
        await self.user_repo.update(user, {"hashed_password": new_hashed_password})
        return True

    async def reset_password(self, email: str, new_password: str, otp: str) -> bool:
        """
        Resets the user's password using an OTP (Mock implementation).
        """
        if not await self.verify_otp(email, otp):
            return False
            
        user = await self.user_repo.get_by_email(email)
        if not user:
            return False
            
        new_hashed_password = self.security.hash_password(new_password)
        await self.user_repo.update(user, {"hashed_password": new_hashed_password})
        return True


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    security: Security = Depends(get_security)
) -> AuthService:
    """
    Dependency function providing a configured instance of AuthService.
    """
    return AuthService(user_repo, security)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.API_V1_STR[1:]}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository),
    security: Security = Depends(get_security)
) -> User:
    """
    Dependency to get the currently authenticated user from a JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = security.decode_jwt_token(token)
    if payload is None:
        raise credentials_exception
        
    email = payload.get("sub")
    if email is None or not isinstance(email, str):
        raise credentials_exception
        
    user = await user_repo.get_by_email(email)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """Ensures the current user is an Admin."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted to administrators."
        )
    return user


async def get_current_vendor(user: User = Depends(get_current_user)) -> User:
    """Ensures the current user is a Vendor."""
    if user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted to vendors."
        )
    return user


async def get_current_customer(user: User = Depends(get_current_user)) -> User:
    """Ensures the current user is a Customer."""
    if user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation restricted to customers."
        )
    return user


class PermissionChecker:
    """
    Dependency that checks if the current user has a specific set of permissions.
    """

    def __init__(self, required_permissions: List[Union[str, PermissionCodename]]):
        # Normalize all permissions to strings
        self.required_permissions = [
            p.value if isinstance(p, PermissionCodename) else p 
            for p in required_permissions
        ]

    async def __call__(
        self,
        user: User = Depends(get_current_user),
        perm_repo: PermissionRepository = Depends(get_permission_repository)
    ) -> User:
        if user.id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in current session."
            )

        effective_permissions = await perm_repo.get_effective_permissions_for_user(user.id)
        missing = [p for p in self.required_permissions if p not in effective_permissions]
        
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(missing)}"
            )
            
        return user
