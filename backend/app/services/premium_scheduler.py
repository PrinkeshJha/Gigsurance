import logging
from datetime import datetime, timedelta
from calendar import month_name
from app.db.database import policies_collection, subscriptions_collection, users_collection
from app.services.risk_engine import recalculate_risk_for_user

logger = logging.getLogger("gigsurance-backend")


async def run_weekly_premium_update():
    """Run weekly premium recalculation and subscription reset."""
    logger.info("Starting weekly premium update")

    # Get current season
    current_month = datetime.utcnow().month
    current_season = month_name[current_month]

    # Get all active policies
    policies = await policies_collection.find({"status": "active"}).to_list(length=None)

    for policy in policies:
        try:
            user_id = policy["user_id"]
            user = await users_collection.find_one({"_id": user_id})
            if not user:
                continue

            # Recalculate risk
            new_risk_data = recalculate_risk_for_user(dict(user), current_season)

            # Update policy
            await policies_collection.update_one(
                {"_id": policy["_id"]},
                {
                    "$set": {
                        "weekly_premium": new_risk_data["weekly_premium"],
                        "risk_score": new_risk_data["risk_score"],
                        "weekly_cap": new_risk_data["weekly_cap"],
                        "per_delivery_deduction": new_risk_data["per_delivery_deduction"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # Create new subscription for this week
            week_start = _get_monday_of_current_week()
            subscription_doc = {
                "user_id": user_id,
                "policy_id": str(policy["_id"]),
                "week_start": week_start,
                "total_deducted_this_week": 0.0,
                "deliveries_count": 0,
                "cap_reached": False,
                "created_at": datetime.utcnow()
            }

            await subscriptions_collection.insert_one(subscription_doc)

            # Create notification
            from app.db.database import notifications_collection
            await notifications_collection.insert_one({
                "user_id": user_id,
                "message": f"Your weekly premium has been recalculated: ₹{new_risk_data['weekly_premium']}",
                "type": "premium_update",
                "read": False,
                "created_at": datetime.utcnow()
            })

        except Exception as e:
            logger.error(f"Failed to update premium for policy {policy['_id']}: {e}")
            continue

    logger.info("Weekly premium update completed")


def _get_monday_of_current_week():
    """Get the Monday of the current week."""
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    return datetime.combine(monday, datetime.min.time())