from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import errors

import app.db.database as database
from app.services.risk_model import calculate_risk_score

from app.schemas.auth import RegisterRequest, LoginRequest, OnboardingCompleteRequest
from app.utils.security import hash_password, verify_password, create_access_token


# -------------------------------
# COLLECTION GETTERS
# -------------------------------

def get_users_collection():
    if database.users_collection is None:
        raise RuntimeError("MongoDB not initialized")
    return database.users_collection


def get_policies_collection():
    if database.policies_collection is None:
        raise RuntimeError("MongoDB not initialized")
    return database.policies_collection


def get_subscriptions_collection():
    if database.subscriptions_collection is None:
        raise RuntimeError("MongoDB not initialized")
    return database.subscriptions_collection


# -------------------------------
# AUTH
# -------------------------------

async def register_user(payload: RegisterRequest):
    users_collection = get_users_collection()

    pan = payload.pan.strip().upper()

    existed = await users_collection.find_one({"pan": pan})
    if existed:
        raise errors.DuplicateKeyError("PAN already registered")

    user_doc = {
        "name": payload.name.strip(),
        "email": payload.email.strip().lower(),
        "mobile": payload.mobile.strip(),
        "pan": pan,
        "platform": "",
        "city": "",
        "zone": "",
        "working_hours": "",
        "role": "user",
        "is_onboarded": False,
        "risk_score": 0,
        "weekly_premium": 0,
        "created_at": datetime.utcnow(),
        "hashed_password": hash_password(payload.password),
    }

    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)

    return user_doc


async def authenticate_user(payload: LoginRequest):
    users_collection = get_users_collection()

    pan = payload.pan.strip().upper()
    user = await users_collection.find_one({"pan": pan})

    if not user:
        return None

    if not verify_password(payload.password, user.get("hashed_password", "")):
        return None

    return user


async def create_user_token(user):
    return create_access_token({
        "pan": user["pan"],
        "role": user.get("role", "user")
    })


# -------------------------------
# RISK
# -------------------------------

def compute_risk(payload):
    user_data = {
        "platform": payload.platform,
        "city": payload.city,
        "zone": payload.zone,
        "working_hours": payload.working_hours
    }
    return calculate_risk_score(user_data)


# -------------------------------
# ONBOARDING
# -------------------------------

async def update_onboarding(pan: str, payload):
    users_collection = get_users_collection()

    update_data = {
        "platform": payload.platform.strip(),
        "zone": payload.zone.strip(),
        "working_hours": payload.working_hours.strip(),
        "is_onboarded": True,
    }

    await users_collection.update_one({"pan": pan}, {"$set": update_data})
    return await users_collection.find_one({"pan": pan})


async def complete_onboarding(user: dict, payload: OnboardingCompleteRequest):
    users_collection = get_users_collection()
    policies_collection = get_policies_collection()
    subscriptions_collection = get_subscriptions_collection()

    if user.get("is_onboarded", False):
        raise errors.InvalidOperation("User already onboarded")

    weekly_cap = round(payload.weekly_premium * 8, 2)
    per_delivery = round(payload.weekly_premium / 35, 2)

    user_update = {
        "platform": payload.platform.strip(),
        "city": payload.city.strip(),
        "zone": payload.zone.strip(),
        "working_hours": payload.working_hours.strip(),
        "risk_score": payload.risk_score,
        "weekly_premium": payload.weekly_premium,
        "is_onboarded": True,
        "updated_at": datetime.utcnow(),
    }

    await users_collection.update_one({"pan": user["pan"]}, {"$set": user_update})

    user_id = str(user["_id"])
    now = datetime.utcnow()

    policy_doc = {
        "user_id": user_id,
        "status": "active",
        "weekly_premium": payload.weekly_premium,
        "risk_score": payload.risk_score,
        "coverage": ["heat", "rain", "civil"],
        "weekly_cap": weekly_cap,
        "per_delivery_deduction": per_delivery,
        "created_at": now,
        "updated_at": now,
    }

    existing = await policies_collection.find_one({"user_id": user_id})

    if existing:
        await policies_collection.update_one({"user_id": user_id}, {"$set": policy_doc})
        policy_id = str(existing["_id"])
    else:
        result = await policies_collection.insert_one(policy_doc)
        policy_id = str(result.inserted_id)

    await subscriptions_collection.insert_one({
        "user_id": user_id,
        "policy_id": policy_id,
        "week_start": _get_monday_of_current_week(),
        "total_deducted_this_week": 0.0,
        "deliveries_count": 0,
        "cap_reached": False,
        "created_at": now,
    })

    return await users_collection.find_one({"pan": user["pan"]})


# -------------------------------
# POLICY (🔥 FIXED KEYS)
# -------------------------------

async def get_policy_for_user(user_id: str):
    policies_collection = get_policies_collection()
    users_collection = get_users_collection()

    policy = await policies_collection.find_one({"user_id": user_id})
    if not policy:
        return None

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    zone = user.get("zone", "") if user else ""

    return {
        "id": str(policy["_id"]),
        "status": policy.get("status", "active"),
        "coverage_amount": policy.get("weekly_cap", 0),
        "weekly_premium": policy.get("weekly_premium", 0),
        "risk_score": policy.get("risk_score", 0),
        "start_date": policy.get("created_at", datetime.utcnow()).isoformat(),
        "zone": zone,
        "triggers": policy.get("coverage", [])
    }


async def toggle_policy_status(user_id: str, active: bool):
    policies_collection = get_policies_collection()
    users_collection = get_users_collection()

    status_value = "active" if active else "paused"

    await policies_collection.update_one(
        {"user_id": user_id},
        {"$set": {"status": status_value}}
    )

    updated = await policies_collection.find_one({"user_id": user_id})
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    zone = user.get("zone", "") if user else ""

    return {
        "id": str(updated["_id"]),
        "status": updated.get("status", "active"),
        "coverage_amount": updated.get("weekly_cap", 0),
        "weekly_premium": updated.get("weekly_premium", 0),
        "risk_score": updated.get("risk_score", 0),
        "start_date": updated.get("created_at", datetime.utcnow()).isoformat(),
        "zone": zone,
        "triggers": updated.get("coverage", [])
    }


# -------------------------------
# PROFILE
# -------------------------------

async def update_profile(pan: str, payload):
    users_collection = get_users_collection()

    update_data = {}

    if payload.name:
        update_data["name"] = payload.name.strip()
    if payload.mobile:
        update_data["mobile"] = payload.mobile.strip()
    if payload.platform:
        update_data["platform"] = payload.platform.strip()
    if payload.zone:
        update_data["zone"] = payload.zone.strip()
    if payload.working_hours:
        update_data["working_hours"] = payload.working_hours.strip()

    if update_data:
        await users_collection.update_one({"pan": pan}, {"$set": update_data})

    return await users_collection.find_one({"pan": pan})


# -------------------------------
# UTILS
# -------------------------------

def _get_monday_of_current_week():
    today = datetime.utcnow().date()
    monday = today - timedelta(days=today.weekday())
    return datetime.combine(monday, datetime.min.time())