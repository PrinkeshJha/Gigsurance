import logging
import json
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from bson import ObjectId
from app.utils.redis_client import redis_client
import numpy as np
from sklearn.cluster import KMeans

from app.config import settings
from app.deps.auth import check_role
from app.db.database import (
    get_users_collection,
    get_policies_collection,
    get_payouts_collection,
    get_triggers_collection
)

# Helpers for dynamic worker locations collection registration matching database.py setups
def get_worker_locations_collection():
    import app.db.database as db
    if getattr(db, "worker_locations_collection", None) is None:
        db.worker_locations_collection = db.db["worker_locations"]
    return db.worker_locations_collection

def get_fraud_logs_collection():
    import app.db.database as db
    if getattr(db, "fraud_logs_collection", None) is None:
        db.fraud_logs_collection = db.db["fraud_logs"]
    return db.fraud_logs_collection

logger = logging.getLogger("gigsurance-backend.geo_analytics")

router = APIRouter(prefix="/analytics", tags=["geospatial-analytics"])

# ---------------------------------------------------------
# HEATMAPS
# ---------------------------------------------------------

@router.get("/heatmap/workers")
async def get_worker_density_heatmap(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    cache_key = "heatmap:workers"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
            
        loc_coll = get_worker_locations_collection()
        pipeline = [
            {
                "$project": {
                    "latitude": {"$arrayElemAt": ["$location.coordinates", 1]},
                    "longitude": {"$arrayElemAt": ["$location.coordinates", 0]},
                    "weight": {"$cond": [{"$eq": ["$is_online", True]}, 1.0, 0.4]}
                }
            }
        ]
        res = await loc_coll.aggregate(pipeline).to_list(length=None)
        
        # Format list
        heatmap_points = [
            {"lat": r["latitude"], "lng": r["longitude"], "weight": r["weight"]}
            for r in res if r.get("latitude") is not None and r.get("longitude") is not None
        ]
        
        # Cache for 60 seconds
        await redis_client.setex(cache_key, 60, json.dumps(heatmap_points))
        return heatmap_points
    except Exception as e:
        logger.exception("Failed to compute worker density heatmap")
        raise HTTPException(status_code=500, detail="Failed to load worker density heatmap.")


@router.get("/heatmap/fraud")
async def get_fraud_hotspots_heatmap(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    cache_key = "heatmap:fraud"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
            
        fraud_coll = get_fraud_logs_collection()
        pipeline = [
            {"$match": {"status": "suspicious"}},
            {
                "$lookup": {
                    "from": "worker_locations",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "loc"
                }
            },
            {"$unwind": "$loc"},
            {
                "$project": {
                    "latitude": {"$arrayElemAt": ["$loc.location.coordinates", 1]},
                    "longitude": {"$arrayElemAt": ["$loc.location.coordinates", 0]},
                    "weight": "$anomaly_score"
                }
            }
        ]
        res = await fraud_coll.aggregate(pipeline).to_list(length=None)
        
        heatmap_points = [
            {"lat": r["latitude"], "lng": r["longitude"], "weight": float(r["weight"]) if r.get("weight") else 1.0}
            for r in res if r.get("latitude") is not None and r.get("longitude") is not None
        ]
        
        await redis_client.setex(cache_key, 60, json.dumps(heatmap_points))
        return heatmap_points
    except Exception as e:
        logger.exception("Failed to compute fraud hotspots heatmap")
        raise HTTPException(status_code=500, detail="Failed to load fraud heatmap.")


@router.get("/heatmap/triggers")
async def get_trigger_activity_heatmap(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    cache_key = "heatmap:triggers"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
            
        triggers_coll = get_triggers_collection()
        pipeline = [
            {
                "$lookup": {
                    "from": "zones",
                    "let": {"z_id": "$zone_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$or": [
                                        {"$eq": ["$_id", "$$z_id"]},
                                        {"$eq": ["$_id", {"$toObjectId": "$$z_id"}]},
                                        {"$eq": [{"$toString": "$_id"}, "$$z_id"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "zone_data"
                }
            },
            {"$unwind": {"path": "$zone_data", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "latitude": "$zone_data.center.lat",
                    "longitude": "$zone_data.center.lon",
                    "weight": {"$literal": 1.0}
                }
            }
        ]
        res = await triggers_coll.aggregate(pipeline).to_list(length=None)
        
        heatmap_points = [
            {"lat": r["latitude"], "lng": r["longitude"], "weight": r["weight"]}
            for r in res if r.get("latitude") is not None and r.get("longitude") is not None
        ]
        
        await redis_client.setex(cache_key, 60, json.dumps(heatmap_points))
        return heatmap_points
    except Exception as e:
        logger.exception("Failed to compute trigger activity heatmap")
        raise HTTPException(status_code=500, detail="Failed to load triggers heatmap.")


@router.get("/heatmap/payouts")
async def get_payouts_heatmap(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    cache_key = "heatmap:payouts"
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
            
        payouts_coll = get_payouts_collection()
        pipeline = [
            {"$match": {"status": "credited"}},
            {
                "$lookup": {
                    "from": "worker_locations",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "loc"
                }
            },
            {"$unwind": {"path": "$loc", "preserveNullAndEmptyArrays": True}},
            {
                "$project": {
                    "latitude": {"$ifNull": [{"$arrayElemAt": ["$loc.location.coordinates", 1]}, 23.0225]},
                    "longitude": {"$ifNull": [{"$arrayElemAt": ["$loc.location.coordinates", 0]}, 72.5714]},
                    "weight": "$amount"
                }
            }
        ]
        res = await payouts_coll.aggregate(pipeline).to_list(length=None)
        
        # Normalize weights so they scale nicely
        max_amount = max([r["weight"] for r in res] + [1.0])
        heatmap_points = [
            {"lat": r["latitude"], "lng": r["longitude"], "weight": float(r["weight"]) / max_amount}
            for r in res if r.get("latitude") is not None and r.get("longitude") is not None
        ]
        
        await redis_client.setex(cache_key, 60, json.dumps(heatmap_points))
        return heatmap_points
    except Exception as e:
        logger.exception("Failed to compute payout distribution heatmap")
        raise HTTPException(status_code=500, detail="Failed to load payout heatmap.")


# ---------------------------------------------------------
# GEO-ZONE STATS
# ---------------------------------------------------------

@router.get("/geo-zones/{id}/stats")
async def get_zone_stats(id: str, admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    try:
        users_coll = get_users_collection()
        payouts_coll = get_payouts_collection()
        triggers_coll = get_triggers_collection()
        
        # Count total workers onboarded in this zone
        total_workers = await users_coll.count_documents({"zone_id": id, "is_onboarded": True})
        
        # Count active triggers for this zone
        active_triggers = await triggers_coll.count_documents({"zone_id": id, "status": "active"})
        
        # Sum total payouts distributed in this zone
        # Payout has user_id, so join payouts with users on user_id where user.zone_id = id
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "_id",
                    "as": "user_data"
                }
            },
            # support string comparison fallback
            {
                "$lookup": {
                    "from": "users",
                    "let": {"u_id": "$user_id"},
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$or": [
                                        {"$eq": ["$_id", "$$u_id"]},
                                        {"$eq": [{"$toString": "$_id"}, "$$u_id"]}
                                    ]
                                }
                            }
                        }
                    ],
                    "as": "user_data_str"
                }
            },
            {
                "$project": {
                    "amount": 1,
                    "status": 1,
                    "zone_id": {
                        "$ifNull": [
                            {"$arrayElemAt": ["$user_data.zone_id", 0]},
                            {"$arrayElemAt": ["$user_data_str.zone_id", 0]}
                        ]
                    }
                }
            },
            {"$match": {"zone_id": id, "status": "credited"}},
            {
                "$group": {
                    "_id": None,
                    "total_payouts": {"$sum": "$amount"},
                    "count_payouts": {"$sum": 1}
                }
            }
        ]
        payout_res = await payouts_coll.aggregate(pipeline).to_list(length=1)
        total_payout_amount = payout_res[0]["total_payouts"] if payout_res else 0.0
        payout_count = payout_res[0]["count_payouts"] if payout_res else 0
        
        return {
            "zone_id": id,
            "total_workers": int(total_workers),
            "active_triggers_count": int(active_triggers),
            "total_payout_amount": float(total_payout_amount),
            "payouts_count": int(payout_count)
        }
    except Exception as e:
        logger.exception(f"Failed to query geo-zone stats for zone {id}")
        raise HTTPException(status_code=500, detail="Failed to load zone statistics.")


# ---------------------------------------------------------
# K-MEANS CLUSTERING ANALYTICS
# ---------------------------------------------------------

@router.get("/workers/clusters")
async def get_worker_clusters(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    try:
        loc_coll = get_worker_locations_collection()
        online_workers = await loc_coll.find({"is_online": True}).to_list(length=None)
        
        if len(online_workers) < 2:
            # Not enough workers to cluster, return coordinates with size 1
            return [
                {
                    "latitude": w["location"]["coordinates"][1],
                    "longitude": w["location"]["coordinates"][0],
                    "size": 1
                }
                for w in online_workers if w.get("location")
            ]
            
        coords = []
        for w in online_workers:
            if not w.get("location"):
                continue
            coord = w["location"]["coordinates"]
            coords.append([coord[1], coord[0]]) # [lat, lon]
            
        if not coords:
            return []
            
        X = np.array(coords)
        
        # Cluster up to 5 groups
        n_clusters = min(5, len(coords))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
        labels = kmeans.fit_predict(X)
        centroids = kmeans.cluster_centers_
        
        clusters = []
        for i in range(n_clusters):
            size = int(np.sum(labels == i))
            clusters.append({
                "latitude": float(centroids[i][0]),
                "longitude": float(centroids[i][1]),
                "size": size
            })
            
        return clusters
    except Exception as e:
        logger.exception("Failed to run K-Means worker clustering analytics")
        raise HTTPException(status_code=500, detail="Failed to process worker spatial clustering.")
