import logging
import httpx
from datetime import datetime, timedelta
from typing import Tuple, Optional, List

from app.config import settings
import app.db.database as database
from app.services import location_service, payout_service

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
    """Run trigger check for all cities."""
    cities = await get_all_cities()

    for city in cities:
        try:
            weather = await fetch_openweather(city)
            temp = weather["main"]["temp"]
            rain = weather.get("rain", {}).get("1h", 0.0)

            heat_triggered = temp > 45.0
            rain_triggered = rain > 12.0

            news_triggered, headline = await fetch_news_trigger(city)

            for condition, trigger_type, value, headline_text in [
                (heat_triggered, "heat", temp, None),
                (rain_triggered, "rain", rain, None),
                (news_triggered, "civil", None, headline),
            ]:
                if condition:
                    await process_trigger(city, trigger_type, value, headline_text)

        except Exception as e:
            logger.error(f"Trigger check failed for {city}: {e}")


# -------------------------------
# WEATHER
# -------------------------------
def _fallback_weather_data(city: str):
    return {"main": {"temp": 30.0}, "rain": {}}


async def fetch_openweather(city: str):
    if not settings.openweather_api_key or settings.openweather_api_key.startswith("dummy"):
        return _fallback_weather_data(city)

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={settings.openweather_api_key}&units=metric"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            res.raise_for_status()
            return res.json()
    except Exception:
        return _fallback_weather_data(city)


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
async def process_trigger(city: str, trigger_type: str, trigger_value, headline):
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")

    try:
        triggers_collection = database.get_triggers_collection()
        result = await triggers_collection.insert_one({
            "type": trigger_type,
            "city": city,
            "date": date_str,
            "value": trigger_value,
            "news_headline": headline,
            "status": "active",
            "timestamp": now
        })
        
        await process_daily_trigger({
            "_id": result.inserted_id,
            "type": trigger_type,
            "city": city,
            "date": date_str,
            "value": trigger_value
        })
    except Exception as e:
        if "duplicate key error" in str(e).lower() or "11000" in str(e):
            pass # Duplicate trigger for today
        else:
            logger.error(f"Error inserting trigger for {city}: {e}")


# -------------------------------
# PAYOUT PROCESSING
# -------------------------------
async def process_daily_trigger(trigger: dict):
    city = trigger["city"]
    trigger_type = trigger["type"]
    trigger_id = trigger["_id"]
    trigger_date = trigger["date"]
    trigger_timestamp = trigger.get("timestamp", datetime.utcnow())

    # Assuming a static trigger location for the city, or passed in the trigger data
    trigger_location = trigger.get("location", {"lat": 23.0225, "lon": 72.5714})

    users = await database.users_collection.find({
        "city": city,
        "is_onboarded": True
    }).to_list(length=None)

    for user in users:
        policy = await database.policies_collection.find_one({
            "user_id": str(user["_id"]),
            "status": "active"
        })

        if not policy or trigger_type not in policy.get("coverage", []):
            continue

        already_paid = await database.payouts_collection.find_one({
            "user_id": user["_id"],
            "trigger_id": str(trigger_id)
        })

        if already_paid:
            continue

        # Fraud Check
        fraud_status, reason = location_service.check_location_validity(user, trigger_location, radius_km=5.0)

        payout_amount = 0.0
        lost_hours = 0.0

        if fraud_status in ("passed", "manual_review"):
            risk_score = float(user.get("risk_score", 50.0))
            payout_result = payout_service.calculate_payout(user, policy, trigger_timestamp, risk_score)
            
            if payout_result["status"] == "rejected":
                if payout_result["reason"] in ("after_work_hours", "no_lost_hours"):
                    continue # Skip silently if it's out of hours
                # If rejected for other reasons, keep 0 payout but log it
            else:
                payout_amount = payout_result["amount"]
                lost_hours = payout_result["lost_hours"]
        else:
            logger.info(f"User {user['_id']} failed fraud check: {reason}")

        if fraud_status == "passed" and payout_amount <= 0:
            continue

        # Store Payout
        await database.payouts_collection.insert_one({
            "user_id": user["_id"],
            "policy_id": policy["_id"],
            "trigger_id": str(trigger_id),
            "trigger_date": trigger_date,
            "amount": payout_amount,
            "lost_hours": lost_hours,
            "trigger_type": trigger_type,
            "status": "credited" if fraud_status == "passed" else "pending",
            "fraud_status": fraud_status,
            "reason": reason,
            "created_at": datetime.utcnow()
        })

        # Notifications
        if fraud_status == "passed":
            await database.notifications_collection.insert_one({
                "user_id": user["_id"],
                "message": f"₹{payout_amount} credited due to {trigger_type} in {city}",
                "type": "payout",
                "read": False,
                "created_at": datetime.utcnow()
            })
        elif fraud_status == "manual_review":
            await database.notifications_collection.insert_one({
                "user_id": user["_id"],
                "message": f"Your payout for {trigger_type} in {city} is under manual review.",
                "type": "payout",
                "read": False,
                "created_at": datetime.utcnow()
            })


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