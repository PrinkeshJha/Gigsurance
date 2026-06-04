import logging
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger("gigsurance-backend")

MONGO_URI = settings.mongo_uri
DB_NAME = settings.db_name

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is required")

# -------------------------------
# GLOBALS
# -------------------------------
client: AsyncIOMotorClient | None = None
db = None

users_collection = None
policies_collection = None
subscriptions_collection = None
trigger_logs_collection = None
triggers_collection = None
premium_history_collection = None
payouts_collection = None
notifications_collection = None
meta_collection = None
delivery_logs_collection = None
zones_collection = None
payout_jobs_collection = None
fraud_logs_collection = None
alerts_collection = None
kyc_logs_collection = None
wallets_collection = None
wallet_transactions_collection = None
withdrawal_requests_collection = None


# -------------------------------
# CONNECT
# -------------------------------
async def connect_to_mongo():
    global client, db
    global users_collection, policies_collection, subscriptions_collection
    global trigger_logs_collection, payouts_collection, notifications_collection
    global triggers_collection, premium_history_collection
    global meta_collection, delivery_logs_collection, zones_collection
    global payout_jobs_collection, fraud_logs_collection, alerts_collection
    global kyc_logs_collection
    global wallets_collection, wallet_transactions_collection, withdrawal_requests_collection

    try:
        client = AsyncIOMotorClient(
            MONGO_URI,
            tls=True,
            tlsCAFile=certifi.where()
        )

        db = client[DB_NAME]

        # Collections
        users_collection = db["users"]
        policies_collection = db["policies"]
        subscriptions_collection = db["subscriptions"]
        trigger_logs_collection = db["trigger_logs"]
        triggers_collection = db["triggers"]
        premium_history_collection = db["premium_history"]
        payouts_collection = db["payouts"]
        notifications_collection = db["notifications"]
        meta_collection = db["meta_locations"]
        delivery_logs_collection = db["delivery_logs"]
        zones_collection = db["zones"]
        payout_jobs_collection = db["payout_jobs"]
        fraud_logs_collection = db["fraud_logs"]
        alerts_collection = db["alerts"]
        kyc_logs_collection = db["kyc_logs"]
        wallets_collection = db["wallets"]
        wallet_transactions_collection = db["wallet_transactions"]
        withdrawal_requests_collection = db["withdrawal_requests"]

        # Ping DB
        await client.admin.command("ping")
        logger.info("✅ MongoDB Connected")

        await create_indexes()

    except Exception as e:
        logger.exception("❌ MongoDB connection failed")
        raise RuntimeError(str(e))


# -------------------------------
# SAFE GETTERS (🔥 IMPORTANT)
# -------------------------------
def get_users_collection():
    if users_collection is None:
        raise RuntimeError("users_collection not initialized")
    return users_collection


def get_policies_collection():
    if policies_collection is None:
        raise RuntimeError("policies_collection not initialized")
    return policies_collection


def get_subscriptions_collection():
    if subscriptions_collection is None:
        raise RuntimeError("subscriptions_collection not initialized")
    return subscriptions_collection


def get_trigger_logs_collection():
    if trigger_logs_collection is None:
        raise RuntimeError("trigger_logs_collection not initialized")
    return trigger_logs_collection


def get_triggers_collection():
    if triggers_collection is None:
        raise RuntimeError("triggers_collection not initialized")
    return triggers_collection


def get_premium_history_collection():
    if premium_history_collection is None:
        raise RuntimeError("premium_history_collection not initialized")
    return premium_history_collection


def get_payouts_collection():
    if payouts_collection is None:
        raise RuntimeError("payouts_collection not initialized")
    return payouts_collection


def get_notifications_collection():
    if notifications_collection is None:
        raise RuntimeError("notifications_collection not initialized")
    return notifications_collection


def get_meta_collection():
    if meta_collection is None:
        raise RuntimeError("meta_collection not initialized")
    return meta_collection


def get_kyc_logs_collection():
    if kyc_logs_collection is None:
        raise RuntimeError("kyc_logs_collection not initialized")
    return kyc_logs_collection


def get_wallets_collection():
    if wallets_collection is None:
        raise RuntimeError("wallets_collection not initialized")
    return wallets_collection


def get_wallet_transactions_collection():
    if wallet_transactions_collection is None:
        raise RuntimeError("wallet_transactions_collection not initialized")
    return wallet_transactions_collection


def get_withdrawal_requests_collection():
    if withdrawal_requests_collection is None:
        raise RuntimeError("withdrawal_requests_collection not initialized")
    return withdrawal_requests_collection


# -------------------------------
# INDEXES
# -------------------------------
async def create_indexes():
    try:
        await users_collection.create_index(
            [("email", 1)],
            name="user_email_unique_idx",
            unique=True
        )

        await users_collection.create_index(
            [("pan", 1)],
            name="user_pan_unique_idx",
            unique=True
        )

        await users_collection.create_index(
            [("kyc_status", 1)],
            name="user_kyc_status_idx"
        )

        await users_collection.create_index(
            [("role", 1)],
            name="user_role_idx"
        )

        await kyc_logs_collection.create_index(
            [("user_id", 1)],
            name="kyc_logs_user_id_idx"
        )

        await kyc_logs_collection.create_index(
            [("user_id", 1), ("created_at", -1)],
            name="kyc_logs_user_created_idx"
        )

        await policies_collection.create_index(
            [("user_id", 1)],
            name="policy_user_id_unique_idx",
            unique=True
        )

        await subscriptions_collection.create_index(
            [("user_id", 1), ("week_start", 1)],
            name="subscription_user_week_idx",
            unique=True
        )

        await delivery_logs_collection.create_index(
            [("user_id", 1), ("timestamp", -1)],
            name="delivery_log_user_time_idx"
        )
        
        await payout_jobs_collection.create_index(
            [("status", 1)],
            name="payout_job_status_idx"
        )
        
        await fraud_logs_collection.create_index(
            [("user_id", 1)],
            name="fraud_log_user_idx"
        )
        
        await alerts_collection.create_index(
            [("zone_id", 1), ("forecast_time", 1)],
            name="alerts_zone_time_idx"
        )

        await trigger_logs_collection.create_index(
            [("city", 1), ("timestamp", -1)],
            name="trigger_city_time_idx"
        )

        await triggers_collection.create_index(
            [("city", 1), ("type", 1), ("date", 1)],
            name="trigger_city_type_date_idx",
            unique=True
        )

        await payouts_collection.create_index(
            [("user_id", 1), ("trigger_log_id", 1)],
            name="payout_unique_idx",
            unique=True
        )

        await notifications_collection.create_index(
            [("user_id", 1), ("read", 1)],
            name="notification_user_read_idx"
        )

        # Wallet System Indexes
        await wallets_collection.create_index(
            [("user_id", 1)],
            name="wallet_user_id_unique_idx",
            unique=True
        )

        await wallet_transactions_collection.create_index(
            [("user_id", 1), ("created_at", -1)],
            name="wallet_tx_user_created_idx"
        )

        await wallet_transactions_collection.create_index(
            [("reference_id", 1)],
            name="wallet_tx_ref_idx"
        )

        await withdrawal_requests_collection.create_index(
            [("user_id", 1)],
            name="withdrawal_user_idx"
        )

        await withdrawal_requests_collection.create_index(
            [("status", 1)],
            name="withdrawal_status_idx"
        )

    except Exception as e:
        if "IndexKeySpecsConflict" not in str(e):
            logger.error(f"Index error: {e}")


# -------------------------------
# CLOSE
# -------------------------------
async def close_mongo_connection():
    global client

    if client:
        client.close()
        logger.info("🔌 MongoDB disconnected")