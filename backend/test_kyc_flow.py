import sys
import os
import asyncio
from datetime import datetime
from bson import ObjectId

# Add current path
sys.path.insert(0, os.path.abspath('.'))

import app.db.database as database
from app.routes.kyc import mask_document_number, release_pending_kyc_payouts
from app.services.deduction_service import process_delivery
from app.services.auth import register_user, complete_onboarding
from app.schemas.auth import RegisterRequest, OnboardingCompleteRequest
from app.schemas.kyc import KycSubmitRequest, KycActionRequest

async def run_tests():
    print("[INFO] Starting KYC & RBAC Integration Tests...")
    
    # 1. Initialize DB
    await database.connect_to_mongo()
    users_coll = database.get_users_collection()
    policies_coll = database.get_policies_collection()
    payouts_coll = database.get_payouts_collection()
    kyc_logs_coll = database.get_kyc_logs_collection()
    notifications_coll = database.get_notifications_collection()

    # Clean up any existing test accounts
    await users_coll.delete_many({"email": {"$in": ["test_auto@gigsurance.com", "test_manual@gigsurance.com"]}})

    # 2. Test Masking Helper
    print("Testing document masking...")
    assert mask_document_number("ABCDE1234F") == "XXXXXX234F"
    assert mask_document_number("123") == "123"
    assert mask_document_number("A") == "A"
    print("[PASS] Document masking works.")

    # 3. Test KYC registration default values
    print("Testing registration default values...")
    payload_auto = RegisterRequest(
        name="Test Auto User",
        email="test_auto@gigsurance.com",
        mobile="9876543210",
        pan="AUTO123456",
        password="password123"
    )
    user_auto = await register_user(payload_auto)
    assert user_auto["kyc_status"] == "uninitiated"
    assert user_auto["role"] == "user"
    assert user_auto["kyc_document_type"] is None
    print("[PASS] Registration default values verified.")

    # 4. Test complete onboarding (Policy should start as pending_kyc since user is not verified)
    print("Testing complete onboarding policy status...")
    onboard_payload = OnboardingCompleteRequest(
        platform="zomato",
        city="mumbai",
        zone="Zone B",
        working_hours="10:00-18:00",
        risk_score=1.2,
        weekly_premium=12.0
    )
    # Complete onboarding
    updated_user = await complete_onboarding(user_auto, onboard_payload)
    
    policy = await policies_coll.find_one({"user_id": str(updated_user["_id"])})
    assert policy is not None
    assert policy["status"] == "pending_kyc", f"Policy should be pending_kyc, got {policy['status']}"
    print("[PASS] Policy status is pending_kyc on onboarding for unverified users.")

    # 5. Test Deduction Service blocks unverified users
    print("Testing deduction service for unverified user...")
    res_deduction = await process_delivery(str(updated_user["_id"]), earnings=150.0)
    assert res_deduction["status"] == "skipped"
    assert res_deduction["reason"] == "kyc_not_verified"
    print("[PASS] Deduction service correctly blocked unverified user.")

    # 6. Test Auto-approval KYC submission (ends with a digit)
    from app.routes.kyc import submit_kyc
    print("Testing automatic KYC approval...")
    
    user_db = await users_coll.find_one({"_id": ObjectId(user_auto["_id"])})
    
    submit_payload = KycSubmitRequest(
        document_type="PAN",
        document_number="PAN1234569" # ends with a digit
    )
    
    res_submit = await submit_kyc(submit_payload, user=user_db)
    assert res_submit["success"] is True
    assert res_submit["message"] == "KYC verified automatically."
    assert res_submit["user"]["kyc_status"] == "verified"
    
    # Verify policy transitioned to active
    policy_after = await policies_coll.find_one({"user_id": str(user_auto["_id"])})
    assert policy_after["status"] == "active"
    print("[PASS] Automatic KYC approval and policy activation verified.")

    # 7. Test Deduction Service works for verified user
    print("Testing deduction service for verified user...")
    # Add expect_deliveries to user for the deduction service
    await users_coll.update_one({"_id": ObjectId(user_auto["_id"])}, {"$set": {"expected_deliveries_per_week": 40, "weekly_cap": 96.0, "deducted_amount": 0.0}})
    res_deduction_active = await process_delivery(str(user_auto["_id"]), earnings=150.0)
    assert res_deduction_active["status"] == "processed"
    print("[PASS] Deduction service successfully processed verified user's delivery.")

    # 8. Test Retroactive payout processing
    print("Testing retroactive payout processing...")
    # Create manual user (ends with letter so stays pending)
    payload_manual = RegisterRequest(
        name="Test Manual User",
        email="test_manual@gigsurance.com",
        mobile="9876543211",
        pan="MANU12345A", # ends in letter 'A'
        password="password123"
    )
    user_manual = await register_user(payload_manual)
    user_manual_db = await users_coll.find_one({"_id": ObjectId(user_manual["_id"])})
    
    # Onboard manual user
    await complete_onboarding(user_manual_db, onboard_payload)
    
    # Submit KYC (should remain pending)
    submit_payload_manual = KycSubmitRequest(
        document_type="PAN",
        document_number="PAN123456A"
    )
    res_submit_manual = await submit_kyc(submit_payload_manual, user=user_manual_db)
    assert res_submit_manual["user"]["kyc_status"] == "pending"

    # Insert a pending_kyc payout
    payout_id = await payouts_coll.insert_one({
        "user_id": str(user_manual["_id"]),
        "policy_id": "test_policy",
        "trigger_id": "test_trigger",
        "amount": 250.0,
        "status": "pending_kyc",
        "created_at": datetime.utcnow()
    })
    
    # Approve KYC manually as admin
    from app.routes.kyc import kyc_action
    action_payload = KycActionRequest(
        user_id=str(user_manual["_id"]),
        action="approve",
        comments="Approved in test suite."
    )
    
    # Mock admin context
    admin_mock = {"role": "admin", "pan": "ADMIN12345"}
    
    res_action = await kyc_action(action_payload, admin=admin_mock)
    assert res_action["success"] is True
    
    # Verify policy became active
    policy_manual = await policies_coll.find_one({"user_id": str(user_manual["_id"])})
    assert policy_manual["status"] == "active"
    
    # Verify the payout was released retroactively to credited
    released_payout = await payouts_coll.find_one({"_id": payout_id.inserted_id})
    assert released_payout["status"] == "credited"
    
    # Verify notification exists
    notification = await notifications_coll.find_one({"user_id": str(user_manual["_id"]), "type": "payout"})
    assert notification is not None
    print("[PASS] Retroactive payout processing verified.")

    # Cleanup
    await users_coll.delete_many({"email": {"$in": ["test_auto@gigsurance.com", "test_manual@gigsurance.com"]}})
    print("[SUCCESS] ALL KYC & RBAC TESTS PASSED!")
    await database.close_mongo_connection()

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except AssertionError as e:
        print(f"[FAIL] Assertion error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        sys.exit(1)
