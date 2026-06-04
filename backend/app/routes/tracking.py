import logging
import asyncio
import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
from bson import ObjectId
from jose import JWTError
from app.utils.redis_client import redis_client
from app.config import settings
from app.deps.auth import get_current_user, check_role
from app.utils.security import decode_access_token
from app.db.database import (
    get_users_collection,
    get_wallets_collection,
    users_collection as global_users_collection
)

# Helpers for database collections matching our registered collection globals
def get_worker_locations_collection():
    from app.db.database import wallets_collection
    # Failsafe if not initialized, but it's initialized on connect_to_mongo
    import app.db.database as db
    if getattr(db, "worker_locations_collection", None) is None:
        db.worker_locations_collection = db.db["worker_locations"]
    return db.worker_locations_collection

def get_location_history_collection():
    import app.db.database as db
    if getattr(db, "location_history_collection", None) is None:
        db.location_history_collection = db.db["location_history"]
    return db.location_history_collection


logger = logging.getLogger("gigsurance-backend.tracking")

router = APIRouter(tags=["tracking"])

# Global registries for local process
active_admin_websockets = set()

# ---------------------------------------------------------
# REDIS PUB/SUB BACKGROUND LISTENER
# ---------------------------------------------------------
async def redis_listener():
    """
    Subscribes to Redis channel and broadcasts coordinates to all local connected admins.
    """
    logger.info("Starting Redis Pub/Sub tracking listener background task...")
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("worker_location_updates")
    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                data_str = message["data"]
                # Broadcast to all locally active admin WebSockets
                for ws in list(active_admin_websockets):
                    try:
                        await ws.send_text(data_str)
                    except Exception:
                        active_admin_websockets.remove(ws)
    except asyncio.CancelledError:
        logger.info("Redis tracking listener background task cancelled.")
    except Exception as e:
        logger.error(f"Error in Redis Pub/Sub tracking listener: {e}")
        # Retry with delay
        await asyncio.sleep(5)
        asyncio.create_task(redis_listener())

@router.on_event("startup")
async def startup_tracking():
    asyncio.create_task(redis_listener())


# ---------------------------------------------------------
# WEBSOCKET ENDPOINTS
# ---------------------------------------------------------

@router.websocket("/ws/worker/location")
async def ws_worker_location(websocket: WebSocket):
    # Extract JWT token from query parameters
    token = websocket.query_params.get("token")
    if not token:
        logger.warning("Rejected WebSocket connection: missing token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        token_data = decode_access_token(token)
        # Verify user
        users_coll = global_users_collection or get_users_collection()
        user = await users_coll.find_one({"pan": token_data.pan})
        if not user:
            logger.warning(f"Rejected WebSocket connection: invalid user for PAN {token_data.pan}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
        user_id = str(user["_id"])
        user_name = user.get("name", "Unknown Worker")
    except Exception as e:
        logger.warning(f"Rejected WebSocket connection: token verification failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    logger.info(f"Accepted tracking connection from worker: {user_name} ({user_id})")

    try:
        while True:
            # Expecting message JSON format: {"latitude": float, "longitude": float, "session_id": str, "is_online": bool}
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            lat = float(data.get("latitude"))
            lon = float(data.get("longitude"))
            session_id = data.get("session_id", "default_session")
            is_online = bool(data.get("is_online", True))
            
            now = datetime.utcnow()

            # 1. Update current location collection
            loc_coll = get_worker_locations_collection()
            await loc_coll.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "location": {
                            "type": "Point",
                            "coordinates": [lon, lat]
                        },
                        "is_online": is_online,
                        "updated_at": now
                    }
                },
                upsert=True
            )

            # 2. Append to location history collection
            hist_coll = get_location_history_collection()
            await hist_coll.insert_one({
                "user_id": user_id,
                "session_id": session_id,
                "location": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "timestamp": now
            })

            # 3. Publish update message to Redis pub/sub channel
            msg = {
                "event": "worker_location_update",
                "data": {
                    "user_id": user_id,
                    "name": user_name,
                    "latitude": lat,
                    "longitude": lon,
                    "is_online": is_online,
                    "updated_at": now.isoformat()
                }
            }
            await redis_client.publish("worker_location_updates", json.dumps(msg))

    except WebSocketDisconnect:
        logger.info(f"Tracking connection disconnected for worker: {user_name}")
        # Update user offline state
        loc_coll = get_worker_locations_collection()
        await loc_coll.update_one(
            {"user_id": user_id},
            {"$set": {"is_online": False, "updated_at": datetime.utcnow()}}
        )
        msg = {
            "event": "worker_status_update",
            "data": {
                "user_id": user_id,
                "name": user_name,
                "is_online": False,
                "updated_at": datetime.utcnow().isoformat()
            }
        }
        await redis_client.publish("worker_location_updates", json.dumps(msg))

    except Exception as e:
        logger.error(f"Error in tracking WebSocket for user {user_id}: {e}")
        await websocket.close()


@router.websocket("/ws/admin/live-map")
async def ws_admin_live_map(websocket: WebSocket):
    # Extract JWT token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        token_data = decode_access_token(token)
        # Verify role is authorized (admin/ops/auditor/claims_agent)
        if token_data.role not in ["admin", "ops", "auditor", "claims_agent"]:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    active_admin_websockets.add(websocket)
    logger.info("Admin connected to real-time live map WebSocket stream.")

    try:
        while True:
            # Admin WebSocket is read-only; keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_admin_websockets.remove(websocket)
        logger.info("Admin disconnected from live map WebSocket stream.")
    except Exception as e:
        logger.error(f"Error in Admin live-map WebSocket: {e}")
        if websocket in active_admin_websockets:
            active_admin_websockets.remove(websocket)


# ---------------------------------------------------------
# REST APIs
# ---------------------------------------------------------

@router.get("/admin/workers/live")
async def get_live_workers(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    """
    REST API to fetch the current active locations of all online workers.
    """
    try:
        loc_coll = get_worker_locations_collection()
        online_workers = await loc_coll.find({"is_online": True}).to_list(length=None)
        
        users_coll = global_users_collection or get_users_collection()
        formatted = []
        for worker in online_workers:
            user_id = worker["user_id"]
            user = await users_coll.find_one({"_id": ObjectId(user_id)})
            
            coords = worker.get("location", {}).get("coordinates", [0.0, 0.0])
            formatted.append({
                "user_id": user_id,
                "name": user.get("name", "Unknown Worker") if user else "Unknown Worker",
                "email": user.get("email", "") if user else "",
                "mobile": user.get("mobile", "") if user else "",
                "latitude": coords[1],  # GeoJSON is [lon, lat]
                "longitude": coords[0],
                "updated_at": worker.get("updated_at").isoformat() if worker.get("updated_at") else None
            })
        return formatted
    except Exception as e:
        logger.exception("Failed to fetch live worker coordinates")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch live workers."
        )


@router.get("/workers/{id}/location/history")
async def get_worker_location_history(id: str, admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    """
    REST API to fetch coordinates history for route playback.
    """
    try:
        hist_coll = get_location_history_collection()
        history = await hist_coll.find({"user_id": id}).sort("timestamp", 1).to_list(length=None)
        
        formatted = []
        for point in history:
            coords = point.get("location", {}).get("coordinates", [0.0, 0.0])
            formatted.append({
                "latitude": coords[1],
                "longitude": coords[0],
                "session_id": point.get("session_id"),
                "timestamp": point.get("timestamp").isoformat() if point.get("timestamp") else None
            })
        return formatted
    except Exception as e:
        logger.exception(f"Failed to fetch historical locations for user {id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch location history."
        )


@router.get("/workers/{id}/location/sessions")
async def get_worker_sessions(id: str, admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    """
    REST API to fetch distinct route session IDs for route replay drop-down selectors.
    """
    try:
        hist_coll = get_location_history_collection()
        sessions = await hist_coll.distinct("session_id", {"user_id": id})
        return sessions
    except Exception as e:
        logger.exception(f"Failed to fetch session list for user {id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch worker sessions."
        )


@router.get("/admin/workers/offline-since/{minutes}")
async def get_offline_workers(minutes: int, admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    """
    REST API to list workers offline for more than X minutes.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        loc_coll = get_worker_locations_collection()
        
        # is_online is False, or online but no update within threshold minutes
        offline_locations = await loc_coll.find({
            "$or": [
                {"is_online": False},
                {"updated_at": {"$lt": cutoff}}
            ]
        }).to_list(length=None)
        
        users_coll = global_users_collection or get_users_collection()
        formatted = []
        for loc in offline_locations:
            user_id = loc["user_id"]
            user = await users_coll.find_one({"_id": ObjectId(user_id)})
            
            coords = loc.get("location", {}).get("coordinates", [0.0, 0.0])
            formatted.append({
                "user_id": user_id,
                "name": user.get("name", "Unknown Worker") if user else "Unknown Worker",
                "email": user.get("email", "") if user else "",
                "mobile": user.get("mobile", "") if user else "",
                "latitude": coords[1],
                "longitude": coords[0],
                "updated_at": loc.get("updated_at").isoformat() if loc.get("updated_at") else None
            })
        return formatted
    except Exception as e:
        logger.exception(f"Failed to fetch offline workers since {minutes} minutes")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch offline workers."
        )
