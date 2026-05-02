import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import (
    get_payouts_collection,
    get_subscriptions_collection
)
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["transactions"])


@router.get("")
async def get_transactions(user=Depends(get_current_user)):
    try:
        # ✅ FIX: SAFE DB ACCESS
        payouts_collection = get_payouts_collection()
        subscriptions_collection = get_subscriptions_collection()

        user_id = user.get("_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )

        user_id_str = str(user_id)

        # -------------------------------
        # FETCH DATA
        # -------------------------------
        payouts = await payouts_collection.find(
            {"user_id": user_id_str}
        ).sort("created_at", -1).to_list(length=None)

        subscriptions = await subscriptions_collection.find(
            {"user_id": user_id_str}
        ).sort("created_at", -1).to_list(length=None)

        transactions = []

        # -------------------------------
        # FORMAT PAYOUTS (CREDIT)
        # -------------------------------
        for p in payouts:
            created_at = p.get("created_at")

            transactions.append({
                "id": str(p.get("_id")),
                "amount": float(p.get("amount", 0)),
                "type": "credit",
                "status": p.get("status", ""),
                "created_at": created_at.isoformat() if created_at else None,
                "_sort_time": created_at
            })

        # -------------------------------
        # FORMAT SUBSCRIPTIONS (DEBIT)
        # -------------------------------
        for s in subscriptions:
            total = float(s.get("total_deducted_this_week", 0))

            if total > 0:
                created_at = s.get("created_at")

                transactions.append({
                    "id": str(s.get("_id")),
                    "amount": -total,
                    "type": "debit",
                    "status": "completed",
                    "created_at": created_at.isoformat() if created_at else None,
                    "_sort_time": created_at
                })

        # -------------------------------
        # SORT PROPERLY
        # -------------------------------
        transactions.sort(
            key=lambda x: x["_sort_time"] or 0,
            reverse=True
        )

        # Remove internal field
        for t in transactions:
            t.pop("_sort_time", None)

        return transactions

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Error fetching transactions: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions"
        )