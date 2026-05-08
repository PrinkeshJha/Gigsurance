from fastapi import APIRouter, HTTPException
import app.db.database as database

router = APIRouter(prefix="/api/fraud", tags=["fraud"])

@router.get("/logs")
async def get_fraud_logs():
    """
    Returns payouts that failed the fraud check and raw ML fraud logs.
    """
    payout_cursor = database.payouts_collection.find({
        "fraud_status": {"$in": ["failed", "manual_review"]}
    }).sort("created_at", -1)
    
    payout_logs = await payout_cursor.to_list(length=50)
    for log in payout_logs:
        log["_id"] = str(log["_id"])
        log["user_id"] = str(log["user_id"])
        log["policy_id"] = str(log["policy_id"])
        
    ml_cursor = database.fraud_logs_collection.find({
        "status": "suspicious"
    }).sort("created_at", -1)
    
    ml_logs = await ml_cursor.to_list(length=50)
    for log in ml_logs:
        log["_id"] = str(log["_id"])
        log["user_id"] = str(log["user_id"])
        
    return {
        "status": "success", 
        "data": {
            "payout_alerts": payout_logs,
            "ml_anomalies": ml_logs
        }
    }
