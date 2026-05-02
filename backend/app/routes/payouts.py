import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List

import app.db.database as database
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["payouts"])

# -------------------------------

# GET PAYOUT HISTORY

# -------------------------------

@router.get("/history")
async def get_payout_history(user: Dict[str, Any] = Depends(get_current_user)):
    try:
        # -------------------------------
        # SAFE COLLECTION ACCESS
        # -------------------------------
        payouts_collection = database.payouts_collection


        if payouts_collection is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )

        # -------------------------------
        # VALIDATE USER
        # -------------------------------
        user_id = str(user.get("_id"))

        if not user_id or user_id == "None":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )

        # -------------------------------
        # FETCH DATA
        # -------------------------------
        payouts = await payouts_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).to_list(length=None)

        # -------------------------------
        # FORMAT DATA (SAFE 🔥)
        # -------------------------------
        formatted: List[Dict[str, Any]] = []

        for p in payouts:
            created_at = p.get("created_at")

            formatted.append({
                "id": str(p.get("_id")),
                "amount": float(p.get("amount", 0)),
                "lost_hours": float(p.get("lost_hours", 0)),
                "status": p.get("status", "unknown"),
                "fraud_status": p.get("fraud_status", "passed"),
                "reason": p.get("reason", ""),
                "created_at": created_at.isoformat() if created_at else None
            })

        # -------------------------------
        # CALCULATIONS
        # -------------------------------
        total_paid = sum(item["amount"] for item in formatted)
        payout_count = len(formatted)

        # -------------------------------
        # RESPONSE
        # -------------------------------
        return {
            "payouts": formatted,
            "total_paid": round(total_paid, 2),
            "payout_count": payout_count
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("❌ Error fetching payout history")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payout history"
        )


@router.get("/{user_id}")
async def get_payouts_for_user(user_id: str):
    """Admin endpoint to fetch payouts for a specific user"""
    try:
        if database.payouts_collection is None:
            raise HTTPException(status_code=500, detail="Database not initialized")
            
        payouts = await database.payouts_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).to_list(length=None)
        
        formatted = []
        for p in payouts:
            created_at = p.get("created_at")
            formatted.append({
                "id": str(p.get("_id")),
                "amount": float(p.get("amount", 0)),
                "lost_hours": float(p.get("lost_hours", 0)),
                "status": p.get("status", "unknown"),
                "fraud_status": p.get("fraud_status", "passed"),
                "reason": p.get("reason", ""),
                "trigger_type": p.get("trigger_type", ""),
                "created_at": created_at.isoformat() if created_at else None
            })
            
        return {"status": "success", "payouts": formatted}
    except Exception as e:
        logger.exception(f"Error fetching payouts for user {user_id}")
        raise HTTPException(status_code=500, detail="Internal server error")
