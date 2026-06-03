import logging
import httpx
from datetime import datetime, timedelta
from typing import Tuple, Optional, List

from app.config import settings
import app.db.database as database
from app.services import location_service, payout_service
from app.tasks.payout_tasks import process_payout_task

logger = logging.getLogger("gigsurance-backend")


# -------------------------------
# GET CITIES (DYNAMIC ✅)
# -------------------------------
async def get_all_cities() -> List[str]:
    doc = await database.meta_collection.find_one({"type": "cities"})
    return doc["data"] if doc else []


# -------------------------------
# MAIN TRIGGER CHECK
# -------------------------------
async def run_trigger_check():
    """Run trigger check for all zones."""
    if database.zones_collection is None:
        return
        
    zones = await database.zones_collection.find({}).to_list(length=None)

    for zone in zones:
        zone_id = str(zone["_id"])
        zone_name = zone.get("name", "Unknown Zone")
        lat = zone.get("center", {}).get("lat", 0.0)
        lon = zone.get("center", {}).get("lon", 0.0)
        
        try:
            weather = await fetch_openweather_by_coords(lat, lon)
            temp = weather["main"]["temp"]
            rain = weather.get("rain", {}).get("1h", 0.0)

            heat_triggered = temp > 45.0
            rain_triggered = rain > 12.0

            # Using zone name for news check as fallback
            news_triggered, headline = await fetch_news_trigger(zone_name)

            for condition, trigger_type, value, headline_text in [
                (heat_triggered, "heat", temp, None),
                (rain_triggered, "rain", rain, None),
                (news_triggered, "civil", None, headline),
            ]:
                if condition:
                    await process_trigger(zone_id, trigger_type, value, headline_text, zone)

        except Exception as e:
            logger.error(f"Trigger check failed for zone {zone_id}: {e}")


# -------------------------------
# WEATHER
# -------------------------------
def _fallback_weather_data():
    return {"main": {"temp": 30.0}, "rain": {}}


async def fetch_openweather_by_coords(lat: float, lon: float):
    if not settings.openweather_api_key or settings.openweather_api_key.startswith("dummy"):
        return _fallback_weather_data()

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.openweather_api_key}&units=metric"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            return res.json()
    except Exception:
        return _fallback_weather_data()


# -------------------------------
# NEWS
# -------------------------------
async def fetch_news_trigger(city: str) -> Tuple[bool, Optional[str]]:
    if not settings.newsapi_key or settings.newsapi_key.startswith("dummy"):
        return False, None

    keywords = "bandh OR curfew OR shutdown OR strike OR protest"
    from_time = (datetime.utcnow() - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S")

    url = f"https://newsapi.org/v2/everything?q={keywords} {city}&language=en&sortBy=publishedAt&from={from_time}&apiKey={settings.newsapi_key}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()

        for article in data.get("articles", []):
            text = (article.get("title", "") + article.get("description", "")).lower()

            if any(k in text for k in ["bandh", "curfew", "strike", "riot", "protest"]):
                return True, article["title"]

        return False, None

    except Exception:
        return False, None


# -------------------------------
# PROCESS TRIGGER
# -------------------------------
async def process_trigger(zone_id: str, trigger_type: str, trigger_value, headline, zone_obj: dict):
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")

    try:
        triggers_collection = database.get_triggers_collection()
        # Prevent duplicates for the same zone, type, and date
        existing = await triggers_collection.find_one({
            "zone_id": zone_id,
            "type": trigger_type,
            "date": date_str
        })
        if existing:
            return

        result = await triggers_collection.insert_one({
            "type": trigger_type,
            "zone_id": zone_id,
            "date": date_str,
            "value": trigger_value,
            "news_headline": headline,
            "status": "active",
            "timestamp": now
        })
        
        await process_daily_trigger({
            "_id": result.inserted_id,
            "type": trigger_type,
            "zone_id": zone_id,
            "date": date_str,
            "value": trigger_value,
            "location": zone_obj.get("center"),
            "radius_km": zone_obj.get("radius_km", 5.0),
            "zone_name": zone_obj.get("name", "Unknown Zone")
        })
    except Exception as e:
        logger.error(f"Error inserting trigger for zone {zone_id}: {e}")


# -------------------------------
# PAYOUT PROCESSING
# -------------------------------
async def process_daily_trigger(trigger: dict):
    zone_id = trigger["zone_id"]
    trigger_type = trigger["type"]
    trigger_id = trigger["_id"]
    trigger_date = trigger["date"]
    trigger_timestamp = trigger.get("timestamp", datetime.utcnow())
    zone_name = trigger.get("zone_name", zone_id)

    # Use trigger zone center directly
    trigger_location = trigger.get("location", {"lat": 23.0225, "lon": 72.5714})
    radius_km = trigger.get("radius_km", 5.0)

    # Ensure Celery task receives serializable data
    trigger_data = {
        "location": trigger_location,
        "radius_km": radius_km,
        "type": trigger_type,
        "date": trigger_date,
        "timestamp": trigger_timestamp.isoformat(),
        "zone_name": zone_name
    }

    users = await database.users_collection.find({
        "zone_id": zone_id,
        "is_onboarded": True
    }).to_list(length=None)

    for user in users:
        # Dispatch to queue instead of processing synchronously
        try:
            process_payout_task.delay(str(user["_id"]), str(trigger_id), trigger_data)
        except Exception as e:
            logger.error(f"Failed to queue payout task for user {user['_id']}: {e}")


# -------------------------------
# PAYOUT CALCULATION
# -------------------------------
def calculate_payout_amount(user: dict, policy: dict) -> float:
    try:
        start_h, end_h = parse_working_hours(user.get("working_hours", ""))

        daily_hours = end_h - start_h
        if daily_hours <= 0:
            return 0.0

        # Convert UTC to IST (+5:30) for accurate working hours check
        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        current_hour = ist_time.hour

        remaining_hours = max(0, end_h - current_hour)

        if remaining_hours <= 0:
            return 0.0

        hourly_income = policy["weekly_cap"] / (5 * daily_hours)

        payout = round(hourly_income * remaining_hours, 2)

        return min(payout, policy["weekly_cap"])

    except Exception as e:
        logger.error(f"Payout error: {e}")
        return 0.0


# -------------------------------
# HELPERS
# -------------------------------
def parse_working_hours(hours_str: str) -> Tuple[int, int]:
    try:
        if not hours_str or "-" not in hours_str:
            return 9, 18

        start, end = hours_str.split("-")
        return int(start.split(":")[0]), int(end.split(":")[0])

    except Exception:
        return 9, 18


async def fraud_check(user: dict, trigger_city: str) -> bool:
    return user.get("city", "").lower() == trigger_city.lower()


# -------------------------------
# LIVE STATUS
# -------------------------------
async def get_live_triggers(user_city: str):
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")

    triggers_collection = database.get_triggers_collection()
    triggers = await triggers_collection.find({
        "city": user_city,
        "status": "active",
        "date": date_str
    }).to_list(length=None)

    if not triggers:
        return {
            "status": "safe",
            "message": f"No active triggers in {user_city} today",
            "last_checked": now.isoformat()
        }

    latest = max(triggers, key=lambda x: x["timestamp"])

    return {
        "status": "active",
        "trigger_type": latest["type"],
        "trigger_value": latest.get("value"),
        "message": f"{latest['type']} trigger active in {user_city}",
        "last_checked": now.isoformat()
    }