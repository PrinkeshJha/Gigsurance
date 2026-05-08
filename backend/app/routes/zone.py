from fastapi import APIRouter
from app.services.zone_service import get_all_zones

router = APIRouter(prefix="/api/zones", tags=["zones"])

@router.get("/")
async def list_zones():
    """List all available parametric zones"""
    zones = await get_all_zones()
    
    formatted = []
    for zone in zones:
        zone_id = str(zone["_id"])
        formatted.append({
            "id": zone_id,
            "name": zone.get("name", zone_id),
            "center": zone.get("center", {}),
            "radius_km": zone.get("radius_km", 5.0)
        })
        
    return {"status": "success", "data": formatted}
