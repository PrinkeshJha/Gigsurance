import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pymongo import errors
from typing import Dict, Any

from app.schemas.auth import (
RegisterRequest,
LoginRequest,
Token,
UserResponse,
MessageResponse,
ProfileUpdateRequest,
)
from app.services.auth import (
register_user,
authenticate_user,
create_user_token,
update_profile,
)
from app.deps.auth import get_current_user, get_current_admin

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["auth"])

# -------------------------------

# REGISTER

# -------------------------------

@router.post(
"/register",
response_model=MessageResponse,
status_code=status.HTTP_201_CREATED
)
async def register(payload: RegisterRequest):
    try:
        await register_user(payload)
        return {"detail": "User registered successfully"}


    except errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists (PAN or email)"
        )

    except Exception as e:
        logger.exception(f"❌ Register failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


# -------------------------------

# LOGIN (IMPORTANT FIX 🔥)

# -------------------------------

@router.post("/login", response_model=Token)
async def login(payload: LoginRequest):
    try:
        # ✅ Authenticate
        user = await authenticate_user(payload)


        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PAN or password"
            )

        # ✅ Generate token
        token = await create_user_token(user)

        # ✅ RETURN CLEAN RESPONSE (FRONTEND DEPENDS ON THIS)
        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


# -------------------------------

# FORMAT USER RESPONSE (SAFE)

# -------------------------------

def format_user_response(user: Dict[str, Any]) -> Dict[str, Any]:
    from datetime import datetime
    kyc_verified_at = user.get("kyc_verified_at")
    if isinstance(kyc_verified_at, datetime):
        kyc_verified_at_str = kyc_verified_at.isoformat()
    elif isinstance(kyc_verified_at, str):
        kyc_verified_at_str = kyc_verified_at
    else:
        kyc_verified_at_str = None

    return {
        "id": str(user.get("_id", "")),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "mobile": user.get("mobile", ""),
        "pan": user.get("pan", ""),
        "platform": user.get("platform", ""),
        "city": user.get("city", ""),
        "zone": user.get("zone", ""),
        "working_hours": user.get("working_hours", ""),
        "role": user.get("role", "user"),
        "is_onboarded": bool(user.get("is_onboarded", False)),
        "risk_score": float(user.get("risk_score", 0)),
        "weekly_premium": float(user.get("weekly_premium", 0)),
        "kyc_status": user.get("kyc_status", "uninitiated"),
        "kyc_verified_at": kyc_verified_at_str,
        "kyc_document_type": user.get("kyc_document_type"),
        "kyc_document_ref": user.get("kyc_document_ref"),
    }

# -------------------------------

# GET CURRENT USER

# -------------------------------

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    try:
        return format_user_response(user)


    except Exception as e:
        logger.exception(f"❌ /auth/me failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )


# -------------------------------

# UPDATE PROFILE

# -------------------------------

@router.patch("/profile", response_model=UserResponse)
async def update_user_profile(
    payload: ProfileUpdateRequest,
    user: dict = Depends(get_current_user)
):
    try:
        updated_user = await update_profile(user.get("pan"), payload)


        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return format_user_response(updated_user)

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


# -------------------------------

# ADMIN CHECK

# -------------------------------

@router.get("/admin-check", response_model=MessageResponse)
async def admin_check(admin: dict = Depends(get_current_admin)):
    return {
        "detail": f"Admin user {admin.get('pan')} authorized"
    }
