import logging
from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId

import app.db.database as database
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["premium"])

@router.get("/{user_id}")
async def get_user_premium(user_id: str, current_user=Depends(get_current_user)):
    try:
        if str(current_user["_id"]) != user_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this premium data"
            )

        users_collection = database.get_users_collection()
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return {
            "user_id": user_id,
            "weekly_premium": user.get("weekly_premium", 0),
            "risk_score": user.get("risk_score", 0),
            "premium_last_updated": user.get("premium_last_updated")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching premium data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch premium data"
        )
