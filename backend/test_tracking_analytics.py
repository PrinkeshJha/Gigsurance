import sys
import os
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException

# Add current path
sys.path.insert(0, os.path.abspath('.'))

import app.db.database as database
from app.routes import tracking, geo_analytics

async def run_tracking_analytics_tests():
    print("[INFO] Starting Tracking & Geospatial Analytics Integration Tests...")
    
    # 1. Initialize DB
    await database.connect_to_mongo()
    users_coll = database.get_users_collection()
    loc_coll = tracking.get_worker_locations_collection()
    hist_coll = tracking.get_location_history_collection()
    fraud_coll = geo_analytics.get_fraud_logs_collection()
    triggers_coll = database.get_triggers_collection()
    payouts_coll = database.get_payouts_collection()

    # Clean up test accounts/data
    test_user_id = str(ObjectId())
    
    # Clean up before testing
    await loc_coll.delete_many({"user_id": test_user_id})
    await hist_coll.delete_many({"user_id": test_user_id})

    # 2. Insert Mock Worker Location
    print("Inserting mock worker locations...")
    lat = 12.9716
    lon = 77.5946
    now = datetime.utcnow()
    
    # online worker
    await loc_coll.insert_one({
        "user_id": test_user_id,
        "location": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "is_online": True,
        "updated_at": now
    })
    
    # offline worker
    test_user_id_2 = str(ObjectId())
    await loc_coll.insert_one({
        "user_id": test_user_id_2,
        "location": {
            "type": "Point",
            "coordinates": [77.6012, 12.9801]
        },
        "is_online": False,
        "updated_at": now - timedelta(minutes=45)
    })

    # 3. Insert Location History
    print("Inserting mock location history...")
    await hist_coll.insert_one({
        "user_id": test_user_id,
        "session_id": "session_test_99",
        "location": {
            "type": "Point",
            "coordinates": [lon, lat]
        },
        "timestamp": now
    })
    await hist_coll.insert_one({
        "user_id": test_user_id,
        "session_id": "session_test_99",
        "location": {
            "type": "Point",
            "coordinates": [lon + 0.001, lat + 0.001]
        },
        "timestamp": now + timedelta(seconds=10)
    })

    # 4. Verify live worker location REST queries
    print("Testing live worker location queries...")
    mock_admin = {"role": "admin"}
    live_workers = await tracking.get_live_workers(admin=mock_admin)
    assert len(live_workers) >= 1
    # Check if our test worker is in there
    found = False
    for w in live_workers:
        if w["user_id"] == test_user_id:
            assert abs(w["latitude"] - lat) < 0.0001
            assert abs(w["longitude"] - lon) < 0.0001
            found = True
    assert found is True
    print("[PASS] Live workers query passes.")

    # 5. Verify location history and sessions REST queries
    print("Testing location history and sessions queries...")
    history = await tracking.get_worker_location_history(id=test_user_id, admin=mock_admin)
    assert len(history) == 2
    assert history[0]["session_id"] == "session_test_99"
    
    sessions = await tracking.get_worker_sessions(id=test_user_id, admin=mock_admin)
    assert "session_test_99" in sessions
    print("[PASS] Location history and sessions queries pass.")

    # 6. Verify offline workers REST query
    print("Testing offline workers query...")
    offline_workers = await tracking.get_offline_workers(minutes=30, admin=mock_admin)
    assert len(offline_workers) >= 1
    found_offline = False
    for w in offline_workers:
        if w["user_id"] == test_user_id_2:
            found_offline = True
    assert found_offline is True
    print("[PASS] Offline workers query passes.")

    # 7. Verify worker density heatmap aggregation
    print("Testing worker density heatmap aggregation...")
    heatmap_workers = await geo_analytics.get_worker_density_heatmap(admin=mock_admin)
    assert len(heatmap_workers) >= 1
    print("[PASS] Worker density heatmap aggregation query passes.")

    # 8. Verify K-Means Clustering Analytics
    print("Testing K-Means Clustering Analytics...")
    clusters = await geo_analytics.get_worker_clusters(admin=mock_admin)
    assert len(clusters) >= 1
    for c in clusters:
        assert "latitude" in c
        assert "longitude" in c
        assert "size" in c
    print("[PASS] K-Means Clustering query passes.")

    # 9. Clean up test documents
    await loc_coll.delete_many({"user_id": {"$in": [test_user_id, test_user_id_2]}})
    await hist_coll.delete_many({"user_id": {"$in": [test_user_id, test_user_id_2]}})
    
    print("[SUCCESS] ALL TRACKING & GEOSPATIAL ANALYTICS TESTS PASSED!")
    await database.close_mongo_connection()

if __name__ == "__main__":
    try:
        asyncio.run(run_tracking_analytics_tests())
    except AssertionError as e:
        print(f"[FAIL] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Test crashed: {e}")
        sys.exit(1)
