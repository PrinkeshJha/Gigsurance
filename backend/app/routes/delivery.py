from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
import app.db.database as database
from app.services.deduction_service import process_delivery

router = APIRouter(prefix="/api/delivery", tags=["delivery"])

class DeliveryInput(BaseModel):
    user_id: str
    earnings: float

@router.post("/")
async def log_delivery(data: DeliveryInput):
    """
    Log a delivery and process micro-deduction.
    """
    result = await process_delivery(data.user_id, data.earnings)
    return result

@router.get("/deductions/{user_id}")
async def get_deductions(user_id: str):
    """
    Get current deduction status for a user.
    """
    try:
        user_id_obj = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id")
        
    user = await database.users_collection.find_one({"_id": user_id_obj})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    weekly_cap = float(user.get("weekly_cap", 0.0))
    deducted_amount = float(user.get("deducted_amount", 0.0))
    deliveries_completed = int(user.get("deliveries_completed", 0))
    
    return {
        "status": "success",
        "data": {
            "weekly_cap": weekly_cap,
            "deducted_amount": deducted_amount,
            "remaining_amount": round(max(0, weekly_cap - deducted_amount), 2),
            "deliveries_completed": deliveries_completed,
            "last_reset": user.get("last_reset")
        }
    }
