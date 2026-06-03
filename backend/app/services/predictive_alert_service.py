import logging
import httpx
from datetime import datetime, timedelta
from app.config import settings
import app.db.database as database

logger = logging.getLogger("gigsurance-backend.alerts")

async def predict_weather_disruptions():
    """
    Fetch forecast for all zones and generate alerts for extreme conditions 
    within the next 48 hours.
    """
    logger.info("Running predictive weather alert job...")
    if database.zones_collection is None:
        return
        
    zones = await database.zones_collection.find({}).to_list(length=None)
    
    if not settings.openweather_api_key or settings.openweather_api_key.startswith("dummy"):
        logger.warning("No OpenWeather API key found. Skipping predictive alerts.")
        return
        
    for zone in zones:
        zone_id = str(zone["_id"])
        lat = zone.get("center", {}).get("lat", 0.0)
        lon = zone.get("center", {}).get("lon", 0.0)
        zone_name = zone.get("name", zone_id)
        
        # 5-day / 3-hour forecast API
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={settings.openweather_api_key}&units=metric"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url)
                res.raise_for_status()
                data = res.json()
                
            # Check the next 48 hours (16 intervals of 3 hours)
            now = datetime.utcnow()
            target_time = now + timedelta(hours=48)
            
            for item in data.get("list", []):
                forecast_dt = datetime.utcfromtimestamp(item["dt"])
                
                if forecast_dt > target_time:
                    break # Only care about next 48 hrs
                    
                temp = item["main"]["temp"]
                rain = item.get("rain", {}).get("3h", 0.0)
                
                alert_type = None
                message = None
                
                if temp > 45.0:
                    alert_type = "heatwave_warning"
                    message = f"Extreme heat ({temp}°C) expected in {zone_name} around {forecast_dt.strftime('%A %H:%M')}."
                elif rain > 20.0:
                    alert_type = "rain_warning"
                    message = f"Heavy rain expected in {zone_name} around {forecast_dt.strftime('%A %H:%M')}."
                    
                if alert_type:
                    # Check if we already alerted for this zone and time
                    existing = await database.alerts_collection.find_one({
                        "zone_id": zone_id,
                        "type": alert_type,
                        "forecast_time": forecast_dt
                    })
                    
                    if not existing:
                        # Create general alert
                        await database.alerts_collection.insert_one({
                            "zone_id": zone_id,
                            "type": alert_type,
                            "message": message,
                            "forecast_time": forecast_dt,
                            "created_at": now
                        })
                        
                        # Notify all users in this zone
                        users = await database.users_collection.find({"zone_id": zone_id, "is_onboarded": True}).to_list(length=None)
                        notifications = []
                        for u in users:
                            notifications.append({
                                "user_id": u["_id"],
                                "message": f"🚨 Predictive Alert: {message}",
                                "type": "warning",
                                "read": False,
                                "created_at": now
                            })
                        if notifications:
                            await database.notifications_collection.insert_many(notifications)
                            
                        logger.info(f"Generated {alert_type} for zone {zone_id}")
        except Exception as e:
            logger.error(f"Failed to fetch forecast for zone {zone_id}: {e}")
