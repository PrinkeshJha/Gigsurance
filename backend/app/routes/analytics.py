import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import (
    get_users_collection,
    get_policies_collection,
    get_payouts_collection
)
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["analytics"])


@router.get("")
async def get_analytics(user=Depends(get_current_user)):
    """Get aggregated analytics data."""
    try:
        # ✅ FIX: SAFE COLLECTION ACCESS
        users_collection = get_users_collection()
        policies_collection = get_policies_collection()
        payouts_collection = get_payouts_collection()

        # -------------------------------
        # TOTAL USERS
        # -------------------------------
        total_users = await users_collection.count_documents({})

        # -------------------------------
        # ACTIVE POLICIES
        # -------------------------------
        active_policies = await policies_collection.count_documents({
            "status": "active"
        })

        # -------------------------------
        # TOTAL PAYOUTS
        # -------------------------------
        total_payouts_result = await payouts_collection.aggregate([
            {"$match": {"status": "credited"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)

        total_payouts = total_payouts_result[0]["total"] if total_payouts_result else 0

        # -------------------------------
        # RISK DISTRIBUTION
        # -------------------------------
        risk_dist = await users_collection.aggregate([
            {"$match": {"is_onboarded": True}},
            {"$group": {"_id": "$risk_score", "count": {"$sum": 1}}}
        ]).to_list(length=None)

        risk_distribution = {
            f"risk_{round(float(r['_id']), 1)}": r["count"]
            for r in risk_dist if r.get("_id") is not None
        }

        # -------------------------------
        # RESPONSE
        # -------------------------------
        return {
            "total_users": int(total_users),
            "active_policies": int(active_policies),
            "total_payouts": round(float(total_payouts), 2),
            "risk_distribution": risk_distribution
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Error fetching analytics: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch analytics"
        )