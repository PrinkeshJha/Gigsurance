import logging
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

from app.schemas.auth import PolicyResponse, PolicyToggleRequest
from app.services.auth import get_policy_for_user, toggle_policy_status
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["policy"])


# -------------------------------
# GET USER POLICY
# -------------------------------
@router.get("/me", response_model=PolicyResponse)
async def get_my_policy(user=Depends(get_current_user)):
    try:
        user_id = user.get("_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session"
            )

        # ✅ FIX: always convert ObjectId → string
        user_id_str = str(user_id)

        policy = await get_policy_for_user(user_id_str)

        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy not found"
            )

        return policy

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Error fetching policy: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch policy"
        )


# -------------------------------
# TOGGLE POLICY
# -------------------------------
@router.post("/toggle", response_model=PolicyResponse)
async def toggle_policy(payload: PolicyToggleRequest, user=Depends(get_current_user)):
    try:
        user_id = user.get("_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session"
            )

        user_id_str = str(user_id)

        policy = await toggle_policy_status(user_id_str, payload.active)

        if not policy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Policy not found"
            )

        return policy

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Error toggling policy: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update policy"
        )