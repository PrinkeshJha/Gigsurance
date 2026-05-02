import logging
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.meta import PLATFORMS
from app.schemas.auth import (
    OnboardingCalculateRequest,
    OnboardingCalculateResponse,
    OnboardingCompleteRequest,
    UserResponse,
)
from app.services.auth import compute_risk, complete_onboarding
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

# ✅ No prefix here (handled in main.py)
router = APIRouter(tags=["onboarding"])


# -------------------------------
# VALIDATION
# -------------------------------
def validate_request(data: OnboardingCalculateRequest):
    if not data.platform or not data.city or not data.zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields"
        )

    if data.platform.strip() not in PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform"
        )


# -------------------------------
# CALCULATE RISK
# -------------------------------
@router.post("/calculate", response_model=OnboardingCalculateResponse)
async def calculate(
    payload: OnboardingCalculateRequest,
    user=Depends(get_current_user)
):
    try:
        validate_request(payload)

        # ✅ CLEAN: risk_engine now returns float
        risk_score = compute_risk(payload)

        if not isinstance(risk_score, (int, float)):
            raise ValueError("Invalid risk_score returned")

        # ✅ BUSINESS LOGIC
        weekly_premium = round(risk_score * 10, 2)
        weekly_cap = round(weekly_premium * 8, 2)
        per_delivery = round(weekly_premium / 35, 2)

        return {
            "risk_score": risk_score,
            "weekly_premium": weekly_premium,
            "weekly_cap": weekly_cap,
            "per_delivery_deduction": per_delivery,
            "breakdown": {
                "platform": payload.platform,
                "city": payload.city,
                "zone": payload.zone,
                "working_hours": payload.working_hours,
                "formula": "premium = risk_score * 10"
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("❌ Error in /onboarding/calculate")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while calculating risk"
        )


# -------------------------------
# COMPLETE ONBOARDING
# -------------------------------
@router.post("/complete", response_model=UserResponse)
async def complete(
    payload: OnboardingCompleteRequest,
    user=Depends(get_current_user)
):
    try:
        validate_request(payload)

        if user.get("is_onboarded", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already onboarded"
            )

        updated_user = await complete_onboarding(user, payload)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete onboarding"
            )

        return updated_user

    except HTTPException:
        raise

    except Exception:
        logger.exception("❌ Error in /onboarding/complete")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during onboarding"
        )