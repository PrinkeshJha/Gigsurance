import asyncio
from datetime import datetime
from bson import ObjectId
import logging

from app.celery_app import celery_app
from app.db.database import connect_to_mongo, close_mongo_connection
import app.db.database as database
from app.services.location_service import check_location_validity
from app.services.payout_service import calculate_payout
from app.services.ml_fraud_service import detect_fraud

logger = logging.getLogger("gigsurance-backend.tasks")

def run_async(coro):
    """Helper to run async code in a synchronous Celery task."""
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

async def _process_payout_async(user_id_str: str, trigger_id_str: str, trigger_data: dict):
    # Connect to MongoDB for this task
    await connect_to_mongo()
    
    try:
        user_id = ObjectId(user_id_str)
        trigger_id = trigger_id_str
        
        # Log job start
        await database.payout_jobs_collection.insert_one({
            "user_id": user_id,
            "trigger_id": trigger_id,
            "status": "processing",
            "created_at": datetime.utcnow()
        })
        
        user = await database.users_collection.find_one({"_id": user_id})
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        policy = await database.policies_collection.find_one({
            "user_id": str(user_id),
            "status": {"$in": ["active", "pending_kyc"]}
        })
        
        if not policy:
            await _update_job_status(user_id, trigger_id, "failed", "No active or pending_kyc policy")
            return
            
        # Extract features for ML model (mocked metrics for now)
        features = {
            "claims_per_week": float(user.get("claims_per_week", 0)),
            "avg_payout_amount": float(user.get("avg_payout_amount", 0)),
            "avg_distance_from_trigger_zone": 0.0,
            "gps_update_frequency": 24.0,
            "payout_frequency": 0.1,
            "trigger_count": float(user.get("trigger_count", 0)),
            "working_hours": 8.0,
            "unusual_activity_score": 0.0
        }
        
        # Fraud Checks
        trigger_location = trigger_data.get("location", {"lat": 23.0225, "lon": 72.5714})
        radius_km = trigger_data.get("radius_km", 5.0)
        
        gps_fraud_status, reason = check_location_validity(user, trigger_location, radius_km=radius_km)
        
        ml_fraud_result = detect_fraud(features)
        ml_status = ml_fraud_result["status"]
        anomaly_score = ml_fraud_result["anomaly_score"]
        
        await database.fraud_logs_collection.insert_one({
            "user_id": user_id,
            "anomaly_score": anomaly_score,
            "status": ml_status,
            "features": features,
            "created_at": datetime.utcnow()
        })
        
        final_fraud_status = gps_fraud_status
        if ml_status == "suspicious" and final_fraud_status == "passed":
            final_fraud_status = "manual_review"
            reason = "Flagged by ML Fraud Detection"
            
        payout_amount = 0.0
        lost_hours = 0.0
        
        trigger_timestamp = trigger_data.get("timestamp", datetime.utcnow())
        
        if final_fraud_status in ("passed", "manual_review"):
            risk_score = float(user.get("risk_score", 50.0))
            payout_result = calculate_payout(user, policy, trigger_timestamp, risk_score)
            
            if payout_result["status"] == "rejected":
                await _update_job_status(user_id, trigger_id, "completed", f"Rejected: {payout_result['reason']}")
                return
            
            payout_amount = payout_result["amount"]
            lost_hours = payout_result["lost_hours"]
            
        if final_fraud_status == "passed" and payout_amount <= 0:
            await _update_job_status(user_id, trigger_id, "completed", "Payout amount 0")
            return
            
        # Store Payout
        is_kyc_pending = (user.get("kyc_status", "uninitiated") != "verified")
        payout_status = "credited" if final_fraud_status == "passed" else "pending"
        if final_fraud_status == "passed" and is_kyc_pending:
            payout_status = "pending_kyc"

        await database.payouts_collection.insert_one({
            "user_id": user_id,
            "policy_id": policy["_id"],
            "trigger_id": trigger_id,
            "trigger_date": trigger_data.get("date"),
            "amount": payout_amount,
            "lost_hours": lost_hours,
            "trigger_type": trigger_data.get("type"),
            "status": payout_status,
            "fraud_status": final_fraud_status,
            "reason": reason,
            "created_at": datetime.utcnow()
        })
        
        # Update user stats
        await database.users_collection.update_one(
            {"_id": user_id},
            {"$inc": {"trigger_count": 1, "avg_payout_amount": payout_amount / 2}}
        )
        
        # Notifications
        if final_fraud_status == "passed":
            if is_kyc_pending:
                await database.notifications_collection.insert_one({
                    "user_id": user_id,
                    "message": f"A payout of ₹{payout_amount} is pending KYC verification. Please complete KYC to release it.",
                    "type": "kyc_alert",
                    "read": False,
                    "created_at": datetime.utcnow()
                })
            else:
                await database.notifications_collection.insert_one({
                    "user_id": user_id,
                    "message": f"₹{payout_amount} credited due to {trigger_data.get('type')} in {trigger_data.get('zone_name', 'your zone')}",
                    "type": "payout",
                    "read": False,
                    "created_at": datetime.utcnow()
                })
            
        await _update_job_status(user_id, trigger_id, "completed", "Success")
        
    finally:
        await close_mongo_connection()

async def _update_job_status(user_id, trigger_id, status, error=None):
    update_doc = {"status": status}
    if error:
        update_doc["error"] = error
        
    await database.payout_jobs_collection.update_one(
        {"user_id": user_id, "trigger_id": trigger_id},
        {"$set": update_doc}
    )

@celery_app.task(bind=True, max_retries=3)
def process_payout_task(self, user_id_str: str, trigger_id_str: str, trigger_data: dict):
    try:
        run_async(_process_payout_async(user_id_str, trigger_id_str, trigger_data))
    except Exception as exc:
        logger.error(f"Task failed for user {user_id_str}: {exc}")
        if self.request.retries == self.max_retries:
            run_async(_update_job_status(ObjectId(user_id_str), trigger_id_str, "failed", str(exc)))
        raise self.retry(exc=exc, countdown=60)
