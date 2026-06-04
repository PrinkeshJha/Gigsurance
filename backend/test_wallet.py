import sys
import os
import asyncio
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException

# Add current path
sys.path.insert(0, os.path.abspath('.'))

import app.db.database as database
from app.services.auth import register_user, complete_onboarding
from app.schemas.auth import RegisterRequest, OnboardingCompleteRequest
from app.routes.kyc import submit_kyc
from app.schemas.kyc import KycSubmitRequest
from app.services import wallet_service

async def run_wallet_tests():
    print("[INFO] Starting Wallet System Integration Tests...")
    
    # 1. Initialize DB
    await database.connect_to_mongo()
    users_coll = database.get_users_collection()
    wallets_coll = database.get_wallets_collection()
    tx_coll = database.get_wallet_transactions_collection()
    withdrawal_coll = database.get_withdrawal_requests_collection()

    # Clean up any existing test accounts
    test_email = "test_wallet_user@gigsurance.com"
    await users_coll.delete_many({"email": test_email})
    await wallets_coll.delete_many({"user_id": {"$exists": True}})
    await tx_coll.delete_many({"user_id": {"$exists": True}})
    await withdrawal_coll.delete_many({"user_id": {"$exists": True}})

    # 2. Register test user
    print("Registering test user...")
    register_payload = RegisterRequest(
        name="Test Wallet User",
        email=test_email,
        mobile="9999888877",
        pan="WALL123456",
        password="password123"
    )
    user = await register_user(register_payload)
    user_id_str = str(user["_id"])
    assert user["kyc_status"] == "uninitiated"
    print("[PASS] User registered.")

    # 3. Complete onboarding
    print("Completing onboarding...")
    onboard_payload = OnboardingCompleteRequest(
        platform="swiggy",
        city="bangalore",
        zone="Zone C",
        working_hours="09:00-17:00",
        risk_score=1.1,
        weekly_premium=15.0
    )
    user_db = await users_coll.find_one({"_id": ObjectId(user_id_str)})
    await complete_onboarding(user_db, onboard_payload)
    print("[PASS] Onboarding completed.")

    # 4. Verify wallet does not exist yet (KYC uninitiated)
    print("Checking wallet pre-KYC...")
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet is None, "Wallet should not exist for uninitiated KYC"
    print("[PASS] Wallet is not pre-provisioned.")

    # 5. Submit KYC with auto-approval (ends in digit)
    print("Submitting KYC for auto-approval...")
    submit_payload = KycSubmitRequest(
        document_type="PAN",
        document_number="PAN9876543" # ends in 3 (digit) -> auto-approve
    )
    user_db_fresh = await users_coll.find_one({"_id": ObjectId(user_id_str)})
    res_submit = await submit_kyc(submit_payload, user=user_db_fresh)
    assert res_submit["success"] is True
    assert res_submit["user"]["kyc_status"] == "verified"
    print("[PASS] KYC approved.")

    # 6. Verify wallet auto-provisioned
    print("Verifying wallet auto-provisioned...")
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet is not None, "Wallet should be created automatically upon KYC approval"
    assert wallet["available_balance"] == 0.0
    assert wallet["pending_balance"] == 0.0
    assert wallet["status"] == "active"
    print("[PASS] Wallet successfully auto-created.")

    # 7. Credit pending payout
    print("Crediting pending payout...")
    payout_amount = 600.0
    payout_id = "payout_test_123"
    trigger_type = "rain"
    wallet_state = await wallet_service.credit_pending(user_id_str, payout_amount, payout_id, trigger_type)
    assert wallet_state["pending_balance"] == payout_amount
    assert wallet_state["available_balance"] == 0.0
    
    # Check transaction log
    tx = await tx_coll.find_one({"user_id": user_id_str, "type": "credit_pending"})
    assert tx is not None
    assert tx["amount"] == payout_amount
    assert tx["status"] == "pending"
    print("[PASS] Pending payout credited and logged in ledger.")

    # 8. Release matured balances (non-matured case)
    print("Running release pending balances (non-matured case)...")
    released_count = await wallet_service.release_pending_balances()
    assert released_count == 0, "No balances should mature yet"
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet["pending_balance"] == payout_amount
    assert wallet["available_balance"] == 0.0
    print("[PASS] Non-matured pending balances remained untouched.")

    # 9. Release matured balances (matured case)
    print("Simulating age of pending credit to 25 hours and running maturity release...")
    # Age the transaction
    old_time = datetime.utcnow() - timedelta(hours=25)
    await tx_coll.update_one({"_id": tx["_id"]}, {"$set": {"created_at": old_time}})
    
    released_count = await wallet_service.release_pending_balances()
    assert released_count == 1, "One pending balance should have matured"
    
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet["pending_balance"] == 0.0
    assert wallet["available_balance"] == payout_amount
    
    # Verify double-entry ledger release transaction
    release_tx = await tx_coll.find_one({"user_id": user_id_str, "type": "release_to_available"})
    assert release_tx is not None
    assert release_tx["amount"] == payout_amount
    print("[PASS] Pending balance successfully matured and moved to available balance.")

    # 10. Withdrawal requests - Insufficient balance check
    print("Testing withdrawal request with insufficient balance...")
    try:
        await wallet_service.request_withdrawal(user_id_str, 1000.0, {"upi_id": "test@upi"})
        assert False, "Should have raised insufficient balance exception"
    except HTTPException as e:
        assert e.status_code == 400
        assert "Insufficient available balance" in e.detail
    print("[PASS] Insufficient balance error caught.")

    # 11. Withdrawal requests - Auto-approval check (<= 10000)
    print("Testing withdrawal request for auto-approved amount (<= 10000)...")
    res_withdraw = await wallet_service.request_withdrawal(user_id_str, 200.0, {"upi_id": "test@upi"})
    assert res_withdraw["status"] == "completed" or res_withdraw["auto_approved"] is True
    
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet["available_balance"] == 400.0  # 600 - 200
    
    # Check logs
    hold_tx = await tx_coll.find_one({"user_id": user_id_str, "type": "withdrawal_hold"})
    complete_tx = await tx_coll.find_one({"user_id": user_id_str, "type": "withdrawal_complete"})
    assert hold_tx is not None
    assert complete_tx is not None
    print("[PASS] Auto-approved withdrawal processed and deducted.")

    # 12. Withdrawal requests - Admin approval required (> 10000)
    print("Adding balance and testing withdrawal request requiring admin approval (> 10000)...")
    await wallets_coll.update_one({"user_id": user_id_str}, {"$inc": {"available_balance": 15000.0}})
    
    res_large_withdraw = await wallet_service.request_withdrawal(user_id_str, 12000.0, {"bank_account": "123", "ifsc": "ABC"})
    assert res_large_withdraw["status"] == "pending_approval"
    assert res_large_withdraw["auto_approved"] is False
    
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet["available_balance"] == 3400.0  # 400 + 15000 - 12000
    print("[PASS] Large withdrawal requested and held in pending_approval.")

    # 13. Admin Approve Withdrawal
    print("Testing admin approval of large withdrawal...")
    withdrawal_id = res_large_withdraw["withdrawal_id"]
    approve_res = await wallet_service.approve_withdrawal(withdrawal_id, "admin_user_99")
    assert approve_res["success"] is True
    
    w_req = await withdrawal_coll.find_one({"_id": ObjectId(withdrawal_id)})
    assert w_req["status"] == "completed"
    assert w_req["admin_reviewer_id"] == "admin_user_99"
    print("[PASS] Admin approval completed.")

    # 14. Admin Reject Withdrawal (refund path)
    print("Testing admin rejection of large withdrawal...")
    # Add balance first
    await wallets_coll.update_one({"user_id": user_id_str}, {"$inc": {"available_balance": 10000.0}})
    
    # Request another large withdrawal
    res_large_withdraw_2 = await wallet_service.request_withdrawal(user_id_str, 11000.0, {"bank_account": "123", "ifsc": "ABC"})
    withdrawal_id_2 = res_large_withdraw_2["withdrawal_id"]
    assert res_large_withdraw_2["status"] == "pending_approval"
    
    reject_res = await wallet_service.reject_withdrawal(withdrawal_id_2, "admin_user_99", "Failed verification checks")
    assert reject_res["success"] is True
    
    w_req_2 = await withdrawal_coll.find_one({"_id": ObjectId(withdrawal_id_2)})
    assert w_req_2["status"] == "rejected"
    assert w_req_2["rejection_reason"] == "Failed verification checks"
    
    # Verify balance was refunded
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet["available_balance"] == 13400.0  # 3400 + 10000 - 11000 + 11000 refund
    print("[PASS] Admin rejection and refund verified.")

    # 15. Freeze wallet check
    print("Testing wallet freeze functionality...")
    await wallet_service.freeze_wallet(user_id_str, True)
    
    wallet = await wallets_coll.find_one({"user_id": user_id_str})
    assert wallet["status"] == "frozen"
    
    # Verify crediting fails
    try:
        await wallet_service.credit_pending(user_id_str, 100.0, "payout_fail", "heat")
        assert False, "Should have failed to credit frozen wallet"
    except wallet_service.WalletError as e:
        assert e.error_code == "WALLET_FROZEN"
        
    # Verify withdrawals fail
    try:
        await wallet_service.request_withdrawal(user_id_str, 50.0, {"upi": "test"})
        assert False, "Should have failed to request withdrawal on frozen wallet"
    except HTTPException as e:
        assert e.status_code == 400
        assert "Wallet is frozen" in e.detail
        
    print("[PASS] Freeze guards verified.")

    # Cleanup
    await users_coll.delete_many({"email": test_email})
    await wallets_coll.delete_many({"user_id": user_id_str})
    await tx_coll.delete_many({"user_id": user_id_str})
    await withdrawal_coll.delete_many({"user_id": user_id_str})
    
    print("[SUCCESS] ALL WALLET TESTS PASSED!")
    await database.close_mongo_connection()

if __name__ == "__main__":
    try:
        asyncio.run(run_wallet_tests())
    except AssertionError as e:
        print(f"[FAIL] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Test crashed: {e}")
        sys.exit(1)
