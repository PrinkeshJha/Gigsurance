from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId
import app.db.database as database

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

    update_doc = {
        "location": {
            "lat": data.lat,
            "lon": data.lon,
            "last_updated": datetime.utcnow()
        }
    }

    result = await database.users_collection.update_one(
        {"_id": user_id_obj},
        {"$set": update_doc}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "success", "message": "Location updated successfully"}
