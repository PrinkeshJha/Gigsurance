import math
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("gigsurance-backend.location")

def calculate_distance_km(coord1: dict, coord2: dict) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    coord1 and coord2 should have 'lat' and 'lon' keys.
    """
    lat1, lon1 = coord1.get("lat"), coord1.get("lon")
    lat2, lon2 = coord2.get("lat"), coord2.get("lon")
    
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')

    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    
    # Radius of earth in kilometers
    r = 6371 
    return c * r

def is_user_in_trigger_zone(user_location: dict, trigger_location: dict, radius_km: float = 5.0) -> bool:
    """
    Check if the user is within the radius of the trigger zone.
    """
    distance = calculate_distance_km(user_location, trigger_location)
    return distance <= radius_km

def check_location_validity(user: dict, trigger_location: dict, radius_km: float = 5.0) -> tuple[str, str]:
    """
    Returns (fraud_status, reason)
    Statuses: "passed", "failed", "manual_review"
    Reasons: "ok", "gps_mismatch", "stale_location", "gps_missing"
    """
    location = user.get("location")
    
    if not location or "lat" not in location or "lon" not in location:
        return "manual_review", "gps_missing"
        
    last_updated = location.get("last_updated")
    if not last_updated:
        return "manual_review", "gps_missing"
        
    # Ensure last_updated is datetime. If string, parse it.
    if isinstance(last_updated, str):
        try:
            last_updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
            # Make naive if it has tzinfo to compare with utcnow
            if last_updated.tzinfo is not None:
                last_updated = last_updated.replace(tzinfo=None)
        except Exception as e:
            logger.error(f"Failed to parse last_updated {last_updated}: {e}")
            return "manual_review", "gps_missing"
            
    now = datetime.utcnow()
    # Check GPS freshness (older than 30 minutes)
    if (now - last_updated) > timedelta(minutes=30):
        return "manual_review", "stale_location"
        
    # Check distance
    if not is_user_in_trigger_zone(location, trigger_location, radius_km):
        return "failed", "gps_mismatch"
        
    return "passed", "ok"
