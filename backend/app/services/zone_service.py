import logging
from typing import Optional
import app.db.database as database
from app.services.location_service import calculate_distance_km

logger = logging.getLogger("gigsurance-backend.zone")

async def get_all_zones():
    """Fetch all zones from the database"""
    if not database.zones_collection:
        return []
    return await database.zones_collection.find({}).to_list(length=None)

async def assign_zone(user_location: dict) -> Optional[str]:
    """
    Given a user_location dict with 'lat' and 'lon', 
    find the nearest zone within its radius_km.
    """
    zones = await get_all_zones()
    
    nearest_zone_id = None
    min_distance = float('inf')
    
    for zone in zones:
        center = zone.get("center", {})
        radius = zone.get("radius_km", 5.0)
        
        distance = calculate_distance_km(user_location, center)
        
        if distance <= radius and distance < min_distance:
            min_distance = distance
            nearest_zone_id = str(zone["_id"])
            
    return nearest_zone_id
