import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.trigger_engine import fetch_openweather
from app.deps.auth import get_current_user

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["weather"])


@router.get("/{zone}")
async def get_weather(zone: str, user=Depends(get_current_user)):
    """Get weather data for a zone."""
    try:
        weather_data = await fetch_openweather(zone)

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