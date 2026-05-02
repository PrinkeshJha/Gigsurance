import logging
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
from bson import ObjectId

import app.db.database as database
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["subscription"])


# -------------------------------
# RECORD DELIVERY
# -------------------------------
@router.post("/record-delivery")
async def record_delivery(user=Depends(get_current_user)):
    try:
        subscriptions_collection = database.subscriptions_collection
        policies_collection = database.policies_collection

        if not subscriptions_collection or not policies_collection:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )

        user_id = str(user.get("_id"))

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )

        week_start = _get_monday_of_current_week()

        # Get subscription
        subscription = await subscriptions_collection.find_one({
            "user_id": user_id,
            "week_start": week_start
        })

        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        if subscription.get("cap_reached"):
            return {
                "deducted": 0.0,
                "message": "Weekly cap reached. This delivery is free.",
                "total_this_week": subscription.get("total_deducted_this_week", 0),
                "cap_reached": True
            }

        # ✅ FIX: Convert to ObjectId
        policy_id = subscription.get("policy_id")
        policy = await policies_collection.find_one({"_id": ObjectId(policy_id)})

        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        deduction = float(policy.get("per_delivery_deduction", 0))
        new_total = float(subscription.get("total_deducted_this_week", 0)) + deduction
        new_count = int(subscription.get("deliveries_count", 0)) + 1

        # ✅ FIX: use weekly_cap
        weekly_cap = float(policy.get("weekly_cap", 0))

        cap_reached = new_total >= weekly_cap
        if cap_reached:
            new_total = weekly_cap

        # Update subscription
        await subscriptions_collection.update_one(
            {"_id": subscription["_id"]},
            {
                "$set": {
                    "total_deducted_this_week": new_total,
                    "deliveries_count": new_count,
                    "cap_reached": cap_reached
                }
            }
        )

        return {
            "deducted": deduction,
            "total_this_week": new_total,
            "cap_reached": cap_reached
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("❌ Error recording delivery")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record delivery"
        )


# -------------------------------
# GET STATUS
# -------------------------------
@router.get("/status")
async def get_subscription_status(user=Depends(get_current_user)):
    try:
        subscriptions_collection = database.subscriptions_collection

        if not subscriptions_collection:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )

        user_id = str(user.get("_id"))

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )

        week_start = _get_monday_of_current_week()

        subscription = await subscriptions_collection.find_one({
            "user_id": user_id,
            "week_start": week_start
        })

        if not subscription:
            return {
                "week_start": week_start.isoformat(),
                "total_deducted_this_week": 0.0,
                "deliveries_count": 0,
                "cap_reached": False
            }

        return {
            "week_start": subscription.get("week_start").isoformat(),
            "total_deducted_this_week": float(subscription.get("total_deducted_this_week", 0)),
            "deliveries_count": int(subscription.get("deliveries_count", 0)),
            "cap_reached": bool(subscription.get("cap_reached", False))
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("❌ Error fetching subscription status")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription status"
        )


# -------------------------------
# UTILS
# -------------------------------
def _get_monday_of_current_week():
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    return datetime.combine(monday, datetime.min.time())