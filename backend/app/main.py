import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers

from app.routes.auth import router as auth_router
from app.routes.meta import router as meta_router
from app.routes.onboarding import router as onboarding_router
from app.routes.policy import router as policy_router
from app.routes.triggers import router as triggers_router
from app.routes.payouts import router as payouts_router
from app.routes.notifications import router as notifications_router
from app.routes.subscription import router as subscription_router
from app.routes.weather import router as weather_router
from app.routes.transactions import router as transactions_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from app.routes.payments import router as payments_router
from app.routes.premium import router as premium_router
from app.routes.location import router as location_router
from app.routes.fraud import router as fraud_router

import app.db.database as database
from app.scheduler import init_scheduler, start_scheduler, shutdown_scheduler
from app.config import settings

# ===============================

# LOGGING

# ===============================

logging.basicConfig(
level=logging.INFO,
format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("gigsurance-backend")

# ===============================

# ENV CONFIG

# ===============================

ENV = "development" if getattr(settings, "debug", True) else "production"

# ===============================

# LIFESPAN

# ===============================

@asynccontextmanager
async def lifespan(app: FastAPI):


    # -------- STARTUP --------
    try:
        await database.connect_to_mongo()

        required_collections = [
            "users_collection",
            "policies_collection",
            "subscriptions_collection",
            "trigger_logs_collection",
            "payouts_collection",
            "notifications_collection"
        ]

        for coll in required_collections:
            if getattr(database, coll, None) is None:
                raise RuntimeError(f"{coll} not initialized")

        logger.info("✅ MongoDB connected")

        # Scheduler
        try:
            init_scheduler()
            await start_scheduler()
            logger.info("✅ Scheduler started")
        except Exception as e:
            logger.warning(f"⚠️ Scheduler failed: {e}")

    except Exception as e:
        logger.exception(f"❌ Startup failed: {e}")
        raise

    yield

    # -------- SHUTDOWN --------
    try:
        await shutdown_scheduler()
    except Exception:
        logger.warning("⚠️ Scheduler shutdown failed")

    try:
        await database.close_mongo_connection()
        logger.info("🔌 MongoDB disconnected")
    except Exception:
        logger.warning("⚠️ MongoDB shutdown issue")

    logger.info("✅ App shutdown complete")


# ===============================

# APP INIT

# ===============================

app = FastAPI(
title="GigSurance Backend",
version="1.0.0",
lifespan=lifespan
)

# ===============================

# 🚨 CRITICAL FIX: CORS (FINAL)

# ===============================

allow_origins = [
"http://localhost:8080",
"http://127.0.0.1:8080",
"http://localhost:8081",
"http://127.0.0.1:8081",
"http://localhost:3000",
]

app.add_middleware(
CORSMiddleware,
allow_origins=allow_origins,   # ❌ DO NOT use "*"
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# ✅ EXTRA FIX: HANDLE PREFLIGHT (VERY IMPORTANT)

@app.options("/{full_path:path}")
async def preflight_handler():
    return {"message": "OK"}

# ===============================

# ROUTES

# ===============================

app.include_router(auth_router, prefix="/auth")
app.include_router(meta_router, prefix="/meta")
app.include_router(onboarding_router, prefix="/onboarding")
app.include_router(policy_router, prefix="/policy")
app.include_router(triggers_router, prefix="/triggers")
app.include_router(payouts_router, prefix="/payout")
app.include_router(payments_router, prefix="/payments")
app.include_router(notifications_router, prefix="/notifications")
app.include_router(subscription_router, prefix="/subscription")
app.include_router(weather_router, prefix="/weather")
app.include_router(transactions_router, prefix="/transactions")
app.include_router(analytics_router, prefix="/analytics")
app.include_router(admin_router, prefix="/admin")
app.include_router(premium_router, prefix="/premium")
app.include_router(location_router) # Uses internal prefix
app.include_router(fraud_router) # Uses internal prefix

# ===============================

# HEALTH CHECK

# ===============================

@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "GigSurance Backend",
        "environment": ENV
    }
