import asyncio
from datetime import datetime
from app.services.risk_engine import calculate_risk_details, _get_seasonal_multiplier
from app.services.trigger_engine import calculate_payout_amount, parse_working_hours

def test_risk_calculation():
    print("--- Testing Risk Engine ---")
    
    # 1. High risk scenario (Delhi, Summer, Peak hours)
    high_risk = calculate_risk_details("blinkit", "delhi", "Zone A", "12:00-22:00")
    print(f"High Risk (Delhi/Blinkit): Score={high_risk['risk_score']}, Premium=Rs.{high_risk['weekly_premium']}, Cap=Rs.{high_risk['weekly_cap']}")
    assert high_risk['risk_score'] > 1.5, "High risk score should be > 1.5"
    
    # 2. Low risk scenario (Unknown city, unknown platform, safe hours)
    low_risk = calculate_risk_details("unknown", "unknown", "Zone C", "06:00-10:00")
    print(f"Low Risk (Unknown/Safe): Score={low_risk['risk_score']}, Premium=Rs.{low_risk['weekly_premium']}, Cap=Rs.{low_risk['weekly_cap']}")
    assert low_risk['risk_score'] < 1.5, "Low risk score should be < 1.5"

    print("SUCCESS: Risk calculation passed\n")


def test_payout_calculation():
    print("--- Testing Payout Calculation ---")
    
    policy = {
        "weekly_cap": 1000.0,
        "weekly_premium": 100.0
    }
    
    # User works 10 to 20 (10 hours)
    user = {
        "working_hours": "10:00-20:00"
    }
    
    # Force UTC hour for testing since calculate_payout_amount uses datetime.utcnow().hour
    current_utc_hour = datetime.utcnow().hour
    
    payout = calculate_payout_amount(user, policy)
    
    start, end = parse_working_hours(user["working_hours"])
    expected_remaining = max(0, end - current_utc_hour)
    
    # 1000 / (5 * 10) = 20 per hour
    expected_payout = 20 * expected_remaining
    
    print(f"Current UTC Hour: {current_utc_hour}")
    print(f"Expected Remaining Hours: {expected_remaining}")
    print(f"Calculated Payout: Rs.{payout}")
    print(f"Expected Payout: Rs.{expected_payout}")
    
    assert payout == expected_payout, f"Payout mismatch. Got {payout}, Expected {expected_payout}"
    
    print("SUCCESS: Payout calculation passed\n")


if __name__ == "__main__":
    try:
        test_risk_calculation()
        test_payout_calculation()
        print("SUCCESS: ALL TESTS PASSED!")
    except AssertionError as e:
        print(f"ERROR: TEST FAILED: {e}")
