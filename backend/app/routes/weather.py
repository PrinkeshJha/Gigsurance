import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.trigger_engine import fetch_openweather_by_coords
from app.deps.auth import get_current_user
import app.db.database as database
from bson import ObjectId

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["weather"])


@router.get("/{zone}")
async def get_weather(zone: str, user=Depends(get_current_user)):
    """Get weather data for a zone."""
    try:
        lat, lon = 0.0, 0.0
        zone_obj = None
        
        if database.zones_collection is not None:
            try:
                zone_obj = await database.zones_collection.find_one({"_id": ObjectId(zone)})
            except Exception:
                # If not a valid ObjectId, try finding by name
                zone_obj = await database.zones_collection.find_one({"name": {"$regex": f"^{zone}$", "$options": "i"}})
                
        if zone_obj and "center" in zone_obj:
            lat = zone_obj["center"].get("lat", 0.0)
            lon = zone_obj["center"].get("lon", 0.0)
            
        weather_data = await fetch_openweather_by_coords(lat, lon)

        if not weather_data:
            raise ValueError("Empty weather response")

        # ✅ SAFE EXTRACTION
        main = weather_data.get("main", {})
        weather_list = weather_data.get("weather", [{}])

        temp = float(main.get("temp", 0))
        condition = weather_list[0].get("main", "Unknown")

        # ✅ RISK LOGIC
        if temp > 40:
            risk_level = "high"
        elif temp > 35:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "temperature": temp,
            "condition": condition,
            "zone": zone,
            "risk_level": risk_level
        }

    except Exception as e:
        logger.exception(f"❌ Weather fetch failed for {zone}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch weather data"
        )