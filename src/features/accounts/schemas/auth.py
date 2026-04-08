from pydantic import BaseModel, EmailStr
from typing import Optional
from src.core.models.user import UserRole


class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    active: bool = True
    verified: bool = False


class VendorProfileRead(BaseModel):
    id: int
    store_name: str
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    user_id: int


class CustomerProfileRead(BaseModel):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    user_id: int


class VendorProfileUpdate(BaseModel):
    store_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class CustomerProfileUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


class UserStatusUpdate(BaseModel):
    active: Optional[bool] = None
    verified: Optional[bool] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.CUSTOMER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str
    otp: str
