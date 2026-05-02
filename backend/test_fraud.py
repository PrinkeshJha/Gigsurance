import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from datetime import datetime, timedelta
from app.services.location_service import check_location_validity, calculate_distance_km
from app.services.payout_service import calculate_payout

def test_location():
    # Ahmedabad city center roughly
    trigger_loc = {"lat": 23.0225, "lon": 72.5714}
    
    # User 1: Very close, fresh GPS
    user1 = {
        "location": {
            "lat": 23.0250,
            "lon": 72.5720,
            "last_updated": datetime.utcnow()
        }
    }
    
    # User 2: Far away (Surat roughly), fresh GPS
    user2 = {
        "location": {
            "lat": 21.1702,
            "lon": 72.8311,
            "last_updated": datetime.utcnow()
        }
    }
    
    # User 3: Close, but stale GPS (1 hour old)
    user3 = {
        "location": {
            "lat": 23.0250,
            "lon": 72.5720,
            "last_updated": datetime.utcnow() - timedelta(hours=1)
        }
    }

    status1, reason1 = check_location_validity(user1, trigger_loc)
    assert status1 == "passed", f"Expected passed, got {status1}: {reason1}"
    
    status2, reason2 = check_location_validity(user2, trigger_loc)
    assert status2 == "failed" and reason2 == "gps_mismatch", f"Expected failed due to distance, got {status2}: {reason2}"
    
    status3, reason3 = check_location_validity(user3, trigger_loc)
    assert status3 == "manual_review" and reason3 == "stale_location", f"Expected manual review due to stale, got {status3}: {reason3}"
    
    print("Location tests passed!")

def test_payout():
    # Setup user
    user = {
        "hourly_rate": 500,
        "working_hours_per_day": 8,
        "working_hours": "09:00-17:00",
        "weekly_cap": 25000
    }
    policy = {"weekly_cap": 25000}
    
    # Trigger at 1 PM (13:00) local time. 
    # Assume trigger_time is matching local time for test simplicity
    trigger_time_1pm = datetime(2023, 1, 1, 13, 0, 0)
    
    payout1 = calculate_payout(user, policy, trigger_time_1pm, risk_score=0.0)
    # Lost hours = 17 - 13 = 4
    # Payout = 4 * 500 * 1.0 = 2000
    assert payout1["amount"] == 2000.0, f"Expected 2000.0, got {payout1['amount']}"
    assert payout1["lost_hours"] == 4.0
    
    # High risk score (100 -> 1.5x multiplier)
    payout2 = calculate_payout(user, policy, trigger_time_1pm, risk_score=100.0)
    # Payout = 4 * 500 * 1.5 = 3000
    assert payout2["amount"] == 3000.0, f"Expected 3000.0, got {payout2['amount']}"

    # Trigger at 6 PM (18:00) -> After work
    trigger_time_6pm = datetime(2023, 1, 1, 18, 0, 0)
    payout3 = calculate_payout(user, policy, trigger_time_6pm, risk_score=0.0)
    assert payout3["status"] == "rejected" and payout3["reason"] == "after_work_hours"
    
    print("Payout tests passed!")

if __name__ == "__main__":
    test_location()
    test_payout()
