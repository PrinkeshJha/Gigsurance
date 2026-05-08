from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
import app.db.database as database
from app.services.zone_service import assign_zone

router = APIRouter(prefix="/api/location", tags=["location"])

class LocationUpdate(BaseModel):
    user_id: str
    lat: float
    lon: float

@router.post("/update")
async def update_location(data: LocationUpdate):
    try:
        user_id_obj = ObjectId(data.user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    loc_dict = {"lat": data.lat, "lon": data.lon}
    
    zone_id = await assign_zone(loc_dict)

    update_doc = {
        "location": {
            "lat": data.lat,
            "lon": data.lon,
            "last_updated": datetime.utcnow()
        }
    }
    
    if zone_id:
        update_doc["zone_id"] = zone_id

    result = await database.users_collection.update_one(
        {"_id": user_id_obj},
        {"$set": update_doc}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "success", "message": "Location updated successfully", "zone_id": zone_id}
