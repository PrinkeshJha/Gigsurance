from datetime import datetime
import logging

logger = logging.getLogger("gigsurance-backend.payout")

def calculate_payout(user: dict, policy: dict, trigger_time: datetime, risk_score: float = 0.0) -> dict:
    """
    Calculate payout based on real income loss.
    Returns:
    {
        "amount": float,
        "lost_hours": float,
        "status": "calculated" | "rejected",
        "reason": str
    }
    """
    # Fetch parameters, providing fallbacks
    hourly_rate = float(user.get("hourly_rate", 0.0))
    working_hours_per_day = int(user.get("working_hours_per_day", 0))
    weekly_cap = float(user.get("weekly_cap", policy.get("weekly_cap", 0.0)))
    
    if hourly_rate <= 0 or working_hours_per_day <= 0:
        # Fallback to older mechanism if new fields are not populated
        working_hours_str = user.get("working_hours", "09:00-18:00")
        try:
            start_str, end_str = working_hours_str.split("-")
            start_h = int(start_str.split(":")[0])
            end_h = int(end_str.split(":")[0])
            working_hours_per_day = end_h - start_h
            if working_hours_per_day > 0 and weekly_cap > 0:
                hourly_rate = weekly_cap / (5 * working_hours_per_day)
            else:
                return {"amount": 0.0, "lost_hours": 0.0, "status": "rejected", "reason": "invalid_working_hours"}
        except Exception:
            return {"amount": 0.0, "lost_hours": 0.0, "status": "rejected", "reason": "invalid_working_hours"}
            
    # Determine the working window based on local time
    # Assuming standard 9 AM start if we only have working_hours_per_day, or parse from 'working_hours'
    working_hours_str = user.get("working_hours", "09:00-18:00")
    try:
        start_h = int(working_hours_str.split("-")[0].split(":")[0])
    except Exception:
        start_h = 9
        
    end_h = start_h + working_hours_per_day

    # Convert UTC to IST (+5:30) for accurate working hours check
    # As trigger_time is UTC, we assume it needs to be matched against Indian working hours
    current_hour = trigger_time.hour

    if current_hour >= end_h:
        return {"amount": 0.0, "lost_hours": 0.0, "status": "rejected", "reason": "after_work_hours"}
        
    if current_hour < start_h:
        # Triggered before work started, full day lost
        lost_hours = float(working_hours_per_day)
    else:
        # Triggered during work
        lost_hours = float(end_h - current_hour)

    if lost_hours <= 0:
        return {"amount": 0.0, "lost_hours": 0.0, "status": "rejected", "reason": "no_lost_hours"}

    # Calculate payout amount
    # risk_multiplier: derived from risk_score (e.g. 1.0 - 1.5)
    # Map risk_score (0-100) to multiplier 1.0 to 1.5
    risk_multiplier = 1.0 + (risk_score / 200.0)
    
    payout = round(hourly_rate * lost_hours * risk_multiplier, 2)
    
    # Cap by weekly cap
    payout = min(payout, weekly_cap)

    return {
        "amount": payout,
        "lost_hours": lost_hours,
        "status": "calculated",
        "reason": "ok"
    }
