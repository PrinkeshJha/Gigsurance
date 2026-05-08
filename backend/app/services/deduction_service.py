import logging
from datetime import datetime
from bson import ObjectId
import app.db.database as database

logger = logging.getLogger("gigsurance-backend.deduction")

async def process_delivery(user_id: str, earnings: float) -> dict:
    """
    Process a micro-deduction per delivery.
    """
    try:
        user_id_obj = ObjectId(user_id)
    except Exception:
        return {"status": "skipped", "reason": "invalid_user_id"}
        
    user = await database.users_collection.find_one({"_id": user_id_obj})
    
    if not user:
        return {"status": "skipped", "reason": "user_not_found"}
        
    if not user.get("is_onboarded", False):
        return {"status": "skipped", "reason": "user_inactive"}
        
    weekly_cap = float(user.get("weekly_cap", 0.0))
    expected_deliveries = int(user.get("expected_deliveries_per_week", 40))
    deducted_amount = float(user.get("deducted_amount", 0.0))
    
    if expected_deliveries <= 0:
        expected_deliveries = 40
        
    # Calculate per delivery deduction
    per_delivery = weekly_cap / expected_deliveries
    
    # Check if we reached the cap
    remaining_amount = weekly_cap - deducted_amount
    
    if remaining_amount <= 0:
        return {"status": "skipped", "reason": "cap_reached"}
        
    # Skip if earnings are too low to deduct from safely
    if earnings < 10.0:
        return {"status": "skipped", "reason": "earnings_too_low"}
        
    deduction = min(per_delivery, remaining_amount)
    
    # Update user stats
    new_deducted = round(deducted_amount + deduction, 2)
    
    await database.users_collection.update_one(
        {"_id": user_id_obj},
        {
            "$set": {"deducted_amount": new_deducted},
            "$inc": {"deliveries_completed": 1}
        }
    )
    
    # Store delivery log
    now = datetime.utcnow()
    await database.delivery_logs_collection.insert_one({
        "user_id": str(user_id_obj),
        "timestamp": now,
        "earnings": earnings,
        "deduction": round(deduction, 2)
    })
    
    return {
        "status": "processed",
        "deduction": round(deduction, 2),
        "new_deducted_total": new_deducted,
        "remaining": round(weekly_cap - new_deducted, 2)
    }

async def reset_weekly_deductions():
    """
    Runs every week via APScheduler.
    Auto-charges the remaining balance if deducted_amount < weekly_cap.
    Resets stats.
    """
    logger.info("Starting weekly deduction reset and top-up...")
    if not database.users_collection:
        return
        
    users = await database.users_collection.find({"is_onboarded": True}).to_list(length=None)
    
    for user in users:
        weekly_cap = float(user.get("weekly_cap", 0.0))
        deducted_amount = float(user.get("deducted_amount", 0.0))
        
        remaining = weekly_cap - deducted_amount
        
        if remaining > 0 and weekly_cap > 0:
            # TODO: Auto-charge via Razorpay here
            logger.info(f"Auto-charging user {user['_id']} for remaining premium: Rs.{remaining}")
            # Mock successful Razorpay call:
            pass
            
        # Reset counters
        await database.users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "deducted_amount": 0.0,
                    "deliveries_completed": 0,
                    "last_reset": datetime.utcnow()
                }
            }
        )
    logger.info("Finished weekly deduction reset.")
