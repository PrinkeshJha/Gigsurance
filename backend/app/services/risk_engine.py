import logging
from typing import Dict, Any

logger = logging.getLogger("gigsurance-backend")


# -------------------------------
# CONSTANTS
# -------------------------------
CITY_FACTORS = {
    "delhi": 0.5,
    "jaipur": 0.5,
    "ahmedabad": 0.5,
    "mumbai": 0.3,
    "kolkata": 0.3,
    "chennai": 0.3,
    "bangalore": 0.2,
    "hyderabad": 0.2,
}

PLATFORM_FACTORS = {
    "blinkit": 0.3,
    "zepto": 0.3,
    "swiggy instamart": 0.2,
    "dunzo": 0.1,
}


# -------------------------------
# MAIN RISK FUNCTION (FIXED 🔥)
# -------------------------------
def calculate_risk(platform: str, city: str, zone: str, working_hours: str) -> float:
    """
    Returns ONLY risk_score (FIXED to avoid dict errors)
    """

    try:
        # Normalize inputs
        platform = (platform or "").lower().strip()
        city = (city or "").lower().strip()

        base_score = 1.0

        city_factor = CITY_FACTORS.get(city, 0.1)
        platform_factor = PLATFORM_FACTORS.get(platform, 0.1)
        hours_factor = _calculate_hours_factor(working_hours)

        risk_score = base_score + city_factor + platform_factor + hours_factor
        risk_score = max(0.5, min(risk_score, 2.5))

        return round(risk_score, 2)

    except Exception as e:
        logger.error(f"Risk calculation error: {e}")
        return 1.0  # safe fallback


# -------------------------------
# OPTIONAL FULL DETAILS (ADVANCED)
# -------------------------------
def calculate_risk_details(platform: str, city: str, zone: str, working_hours: str) -> Dict[str, Any]:
    """
    Returns full breakdown (optional use)
    """
    risk_score = calculate_risk(platform, city, zone, working_hours)

    city = (city or "").lower().strip()
    platform = (platform or "").lower().strip()

    city_factor = CITY_FACTORS.get(city, 0.1)
    platform_factor = PLATFORM_FACTORS.get(platform, 0.1)
    hours_factor = _calculate_hours_factor(working_hours)

    return _build_risk_response(risk_score, city_factor, hours_factor, platform_factor)


# -------------------------------
# COMMON BUILDER
# -------------------------------
def _build_risk_response(
    risk_score: float,
    city_factor: float,
    hours_factor: float,
    platform_factor: float
) -> Dict[str, Any]:

    weekly_premium = round(50 + (risk_score * 40), 2)
    weekly_cap = round(weekly_premium * 8, 2)
    per_delivery = round(weekly_premium / 35, 2)

    return {
        "risk_score": risk_score,
        "weekly_premium": weekly_premium,
        "weekly_cap": weekly_cap,
        "per_delivery_deduction": per_delivery,
        "breakdown": {
            "city_factor": city_factor,
            "hours_factor": hours_factor,
            "platform_factor": platform_factor,
        }
    }


# -------------------------------
# HOURS FACTOR
# -------------------------------
def _calculate_hours_factor(working_hours: str) -> float:
    try:
        if not working_hours or "-" not in working_hours:
            return 0.2

        start_str, end_str = working_hours.split("-")

        start_hour = int(start_str.split(":")[0])
        end_hour = int(end_str.split(":")[0])

        peak_start, peak_end = 11, 16

        overlap_start = max(start_hour, peak_start)
        overlap_end = min(end_hour, peak_end)
        overlap = max(0, overlap_end - overlap_start)

        if overlap >= 2:
            return 0.4
        elif start_hour < 10 or end_hour > 19:
            return 0.1
        else:
            return 0.2

    except Exception:
        logger.warning(f"Invalid working_hours: {working_hours}")
        return 0.2


# -------------------------------
# RE-CALCULATION (SAFE)
# -------------------------------
def recalculate_risk_for_user(user: Dict[str, Any], current_season: str = None) -> Dict[str, Any]:
    try:
        risk_data = calculate_risk_details(
            user.get("platform", ""),
            user.get("city", ""),
            user.get("zone", ""),
            user.get("working_hours", "")
        )

        if current_season:
            multiplier = _get_seasonal_multiplier(user.get("city", ""), current_season)

            new_score = risk_data["risk_score"] + multiplier
            new_score = max(0.5, min(new_score, 2.5))

            return _build_risk_response(
                new_score,
                risk_data["breakdown"]["city_factor"],
                risk_data["breakdown"]["hours_factor"],
                risk_data["breakdown"]["platform_factor"]
            )

        return risk_data

    except Exception as e:
        logger.error(f"Recalculate risk error: {e}")
        return {
            "risk_score": 1.0,
            "weekly_premium": 90,
            "weekly_cap": 720,
            "per_delivery_deduction": 2.5,
            "breakdown": {}
        }


# -------------------------------
# SEASONAL FACTOR
# -------------------------------
def _get_seasonal_multiplier(city: str, season: str) -> float:
    city = (city or "").lower()

    summer = {"delhi", "jaipur", "ahmedabad"}
    monsoon = {"mumbai", "kolkata", "chennai"}

    if season in ["April", "May", "June"]:
        return 0.3 if city in summer else 0.1
    elif season in ["June", "July", "August", "September"]:
        return 0.3 if city in monsoon else 0.1

    return 0.0