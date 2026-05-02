import logging
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta

import app.db.database as database
from app.deps.auth import get_current_admin

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["admin"])


@router.get("/kpis")
async def get_admin_kpis(admin=Depends(get_current_admin)):
    """Get admin dashboard metrics."""
    try:
        # ✅ SAFE COLLECTION ACCESS
        users_collection = database.users_collection
        payouts_collection = database.payouts_collection

        if not users_collection or not payouts_collection:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database not initialized"
            )

        # -------------------------------
        # REVENUE
        # -------------------------------
        revenue_result = await payouts_collection.aggregate([
            {"$match": {"status": "credited"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(length=1)

        revenue = revenue_result[0]["total"] if revenue_result else 0

        # -------------------------------
        # ACTIVE USERS
        # -------------------------------
        active_users = await users_collection.count_documents({
            "is_onboarded": True
        })

        # -------------------------------
        # CLAIMS PROCESSED
        # -------------------------------
        claims_processed = await payouts_collection.count_documents({
            "status": "credited"
        })

        # -------------------------------
        # GROWTH RATE
        # -------------------------------
        now = datetime.utcnow()
        this_month = now.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)

        this_month_users = await users_collection.count_documents({
            "created_at": {"$gte": this_month}
        })

        last_month_users = await users_collection.count_documents({
            "created_at": {"$gte": last_month, "$lt": this_month}
        })

        # ✅ SAFE DIVISION
        if last_month_users > 0:
            growth_rate = ((this_month_users - last_month_users) / last_month_users) * 100
        else:
            growth_rate = 0.0

        # -------------------------------
        # RESPONSE
        # -------------------------------
        return {
            "revenue": round(float(revenue), 2),
            "active_users": int(active_users),
            "claims_processed": int(claims_processed),
            "growth_rate": round(float(growth_rate), 2)
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("❌ Error fetching admin KPIs")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch admin KPIs"
        )