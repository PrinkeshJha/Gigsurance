import logging
from datetime import datetime
import app.db.database as database
from app.services.risk_model import calculate_risk_score

logger = logging.getLogger("gigsurance-backend")

BASE_PREMIUM_COST = 20.0

async def update_all_user_premiums():
    """
    Recalculates premium for all users based on their latest risk score.
    Runs every 7 days.
    """
    logger.info("Starting global premium update for all users.")
    try:
        users_collection = database.get_users_collection()
        premium_history_collection = database.db["premium_history"]
        policies_collection = database.get_policies_collection()

        users = await users_collection.find({"is_onboarded": True}).to_list(length=None)

        updated_count = 0
        for user in users:
            try:
                user_id = str(user["_id"])
                
                # Recalculate risk score just in case
                risk_score = calculate_risk_score(user)
                
                new_premium = round(BASE_PREMIUM_COST * risk_score, 2)
                now = datetime.utcnow()
                
                # Update User Document
                await users_collection.update_one(
                    {"_id": user["_id"]},
                    {
                        "$set": {
                            "risk_score": risk_score,
                            "weekly_premium": new_premium,
                            "premium_last_updated": now
                        }
                    }
                )
                
                # Update Policy Document
                weekly_cap = round(new_premium * 8, 2)
                per_delivery = round(new_premium / 35, 2)
                
                await policies_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "weekly_premium": new_premium,
                            "risk_score": risk_score,
                            "weekly_cap": weekly_cap,
                            "per_delivery_deduction": per_delivery,
                            "updated_at": now
                        }
                    }
                )
                
                # Maintain Premium History
                await premium_history_collection.insert_one({
                    "user_id": user_id,
                    "risk_score": risk_score,
                    "weekly_premium": new_premium,
                    "calculated_at": now
                })
                
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update premium for user {user.get('_id')}: {e}")

        logger.info(f"Global premium update completed. Updated {updated_count} users.")
    except Exception as e:
        logger.exception(f"Fatal error during global premium update: {e}")
