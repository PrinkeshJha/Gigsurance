from fastapi import APIRouter, HTTPException
import app.db.database as database

router = APIRouter(prefix="/api/fraud", tags=["fraud"])

@router.get("/logs")
async def get_fraud_logs():
    """
    Returns payouts that failed the fraud check or need manual review.
    """
    cursor = database.payouts_collection.find({
        "fraud_status": {"$in": ["failed", "manual_review"]}
    }).sort("created_at", -1)
    
    logs = await cursor.to_list(length=100)
    
    # Convert ObjectIds to string for JSON serialization
    for log in logs:
        log["_id"] = str(log["_id"])
        log["user_id"] = str(log["user_id"])
        log["policy_id"] = str(log["policy_id"])
        
    return {"status": "success", "data": logs}
