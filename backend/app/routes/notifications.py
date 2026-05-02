import logging
from fastapi import APIRouter, Depends, HTTPException, status

import app.db.database as database
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["notifications"])


# -------------------------------
# GET NOTIFICATIONS
# -------------------------------
@router.get("")
async def get_notifications(user=Depends(get_current_user)):
    try:
        notifications_collection = database.notifications_collection

        if not notifications_collection:
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

        notifications = await notifications_collection.find(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        ).to_list(length=None)

        # ✅ FIX: serialize ObjectId
        formatted = [
            {
                "id": str(n.get("_id")),
                "type": n.get("type", "info"),
                "title": n.get("title", ""),
                "message": n.get("message", ""),
                "read": n.get("read", False),
                "timestamp": n.get("created_at").isoformat() if n.get("created_at") else None
            }
            for n in notifications
        ]

        return formatted

    except HTTPException:
        raise

    except Exception:
        logger.exception("❌ Error fetching notifications")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notifications"
        )


# -------------------------------
# MARK AS READ
# -------------------------------
@router.post("/mark-read")
async def mark_notifications_read(user=Depends(get_current_user)):
    try:
        notifications_collection = database.notifications_collection

        if not notifications_collection:
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

        result = await notifications_collection.update_many(
            {"user_id": user_id, "read": False},
            {"$set": {"read": True}}
        )

        return {
            "success": True,
            "marked_read": result.modified_count
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("❌ Error marking notifications")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notifications"
        )