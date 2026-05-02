import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.trigger_engine import get_live_triggers
from app.deps.auth import get_current_user
from app.db.database import get_triggers_collection

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["triggers"])


# -------------------------------
# LIVE TRIGGER STATUS
# -------------------------------
@router.get("/live")
async def get_live_triggers_endpoint(user=Depends(get_current_user)):
    try:
        user_city = user.get("city", "")

        if not user_city:
            return {
                "status": "safe",
                "trigger_type": None,
                "trigger_value": None,
                "message": "User city not set.",
                "last_checked": None
            }

        return await get_live_triggers(user_city)

    except Exception as e:
        logger.exception(f"❌ Error fetching live triggers: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch live triggers"
        )


# -------------------------------
# GET ALL TRIGGERS
# -------------------------------
@router.get("/all")
async def get_all_triggers(user=Depends(get_current_user)):
    try:
        # ✅ FIX: SAFE DB ACCESS
        collection = get_triggers_collection()

        triggers = await collection.find(
            {"status": "active"}
        ).sort("timestamp", -1).to_list(length=None)

        return [format_trigger(t) for t in triggers]

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Error fetching triggers: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch triggers"
        )


# -------------------------------
# GET TRIGGERS BY ZONE
# -------------------------------
@router.get("/{zone}")
async def get_triggers_by_zone(zone: str, user=Depends(get_current_user)):
    try:
        collection = get_triggers_collection()

        triggers = await collection.find(
            {"city": zone, "status": "active"}
        ).sort("timestamp", -1).to_list(length=None)

        return [format_trigger(t) for t in triggers]

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f"❌ Error fetching triggers by zone: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch triggers"
        )


# -------------------------------
# FORMAT HELPER
# -------------------------------
def format_trigger(t: dict):
    value = t.get("value")

    # ✅ SAFE severity logic
    if isinstance(value, (int, float)):
        severity = "high" if value > 40 else "medium"
    else:
        severity = "medium"

    timestamp = t.get("timestamp")

    return {
        "id": str(t.get("_id")),
        "type": t.get("type", ""),
        "zone": t.get("city", ""),
        "date": t.get("date", ""),
        "severity": severity,
        "timestamp": timestamp.isoformat() if timestamp else None
    }