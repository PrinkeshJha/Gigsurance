from fastapi import APIRouter, HTTPException
from bson import ObjectId
import app.db.database as database

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

@router.get("/{user_id}")
async def get_user_alerts(user_id: str):
    """
    Get predictive weather disruption alerts for the user's current zone.
    """
    try:
        user_id_obj = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
        
    user = await database.users_collection.find_one({"_id": user_id_obj})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    zone_id = user.get("zone_id")
    if not zone_id:
        return {"status": "success", "data": [], "message": "User not assigned to any zone"}
        
    cursor = database.alerts_collection.find({
        "zone_id": zone_id
    }).sort("forecast_time", 1)
    
    alerts = await cursor.to_list(length=20)
    for alert in alerts:
        alert["_id"] = str(alert["_id"])
        
    return {"status": "success", "data": alerts}
