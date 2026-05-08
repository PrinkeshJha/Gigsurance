import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.trigger_engine import run_trigger_check
from app.services.premium_service import update_all_user_premiums
from app.services.deduction_service import reset_weekly_deductions
from app.services.predictive_alert_service import predict_weather_disruptions

logger = logging.getLogger("gigsurance-backend")

scheduler = AsyncIOScheduler()


# -------------------------------
# INIT (FIXED ✅ no duplicates)
# -------------------------------
def init_scheduler():
    """Initialize scheduler safely (no duplicate jobs)."""

    if scheduler.get_job("trigger_check"):
        return  # already initialized

    # Trigger check every 10 minutes
    scheduler.add_job(
        run_trigger_check,
        trigger=IntervalTrigger(minutes=10),
        id="trigger_check",
        max_instances=1,
        replace_existing=True
    )

    # Weekly premium update
    scheduler.add_job(
        update_all_user_premiums,
        trigger="cron",
        day_of_week="mon",
        hour=0,
        minute=1,
        id="weekly_premium_update",
        max_instances=1,
        replace_existing=True
    )

    # Weekly deduction reset and top-up
    scheduler.add_job(
        reset_weekly_deductions,
        trigger="cron",
        day_of_week="mon",
        hour=0,
        minute=1,
        id="weekly_deduction_reset",
        max_instances=1,
        replace_existing=True
    )

    # Predictive weather alerts every 6 hours
    scheduler.add_job(
        predict_weather_disruptions,
        trigger=IntervalTrigger(hours=6),
        id="predictive_weather_alerts",
        max_instances=1,
        replace_existing=True
    )

    # ❌ removed noisy log


# -------------------------------
# START (CLEAN)
# -------------------------------
async def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("✅ Scheduler Started")


# -------------------------------
# SHUTDOWN
# -------------------------------
async def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🔴 Scheduler Stopped")