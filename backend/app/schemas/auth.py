from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List


# -------------------------------
# AUTH
# -------------------------------
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    mobile: str = Field(..., min_length=10, max_length=15)
    pan: str = Field(..., min_length=10, max_length=10)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    pan: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    pan: Optional[str] = None
    role: Optional[str] = None


# -------------------------------
# USER
# -------------------------------
class UserResponse(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    mobile: str
    pan: str

    platform: Optional[str] = ""
    city: Optional[str] = ""
    zone: Optional[str] = ""
    working_hours: Optional[str] = ""

    role: str = "user"
    is_onboarded: bool = False

    risk_score: float = 0.0          # ✅ FIXED
    weekly_premium: float = 0.0      # ✅ FIXED

    kyc_status: str = "uninitiated"
    kyc_verified_at: Optional[str] = None
    kyc_document_type: Optional[str] = None
    kyc_document_ref: Optional[str] = None


# -------------------------------
# META
# -------------------------------
class CityResponse(BaseModel):
    city: str
    zones: List[str]


# -------------------------------
# ONBOARDING
# -------------------------------
class OnboardingCalculateRequest(BaseModel):
    platform: str
    city: str
    zone: str
    working_hours: str


class OnboardingCalculateResponse(BaseModel):
    risk_score: float
    weekly_premium: float
    weekly_cap: float
    per_delivery_deduction: float
    breakdown: Dict[str, Any]


class OnboardingCompleteRequest(BaseModel):
    platform: str
    city: str
    zone: str
    working_hours: str
    risk_score: float              # ✅ FIXED
    weekly_premium: float          # ✅ FIXED


# -------------------------------
# POLICY
# -------------------------------
class PolicyResponse(BaseModel):
    id: str
    status: str
    coverage_amount: float         # ✅ FIXED
    weekly_premium: float          # ✅ FIXED
    risk_score: float              # ✅ FIXED
    start_date: str
    zone: str
    triggers: List[str]


class PolicyToggleRequest(BaseModel):
    active: bool


# -------------------------------
# PROFILE
# -------------------------------
class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    platform: Optional[str] = None
    zone: Optional[str] = None
    working_hours: Optional[str] = None


# -------------------------------
# COMMON
# -------------------------------
class MessageResponse(BaseModel):
    detail: str