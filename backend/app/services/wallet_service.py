import logging
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
from typing import Dict, Any, List

from app.db.database import (
    get_wallets_collection,
    get_wallet_transactions_collection,
    get_withdrawal_requests_collection,
    get_users_collection
)

logger = logging.getLogger("gigsurance-backend.wallet")

class WalletError(Exception):
    def __init__(self, message: str, error_code: str = "WALLET_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


async def create_wallet(user_id: str) -> Dict[str, Any]:
    wallets_coll = get_wallets_collection()
    
    # Check if wallet already exists
    existing = await wallets_coll.find_one({"user_id": user_id})
    if existing:
        return existing
        
    now = datetime.utcnow()
    wallet_doc = {
        "user_id": user_id,
        "available_balance": 0.0,
        "pending_balance": 0.0,
        "status": "active",
        "created_at": now,
        "updated_at": now
    }
    
    try:
        await wallets_coll.insert_one(wallet_doc)
        logger.info(f"Wallet successfully created for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to create wallet for user {user_id}: {e}")
        raise WalletError("Failed to create wallet", "WALLET_CREATION_FAILED")
        
    return wallet_doc


async def get_wallet_by_user(user_id: str) -> Dict[str, Any]:
    wallets_coll = get_wallets_collection()
    wallet = await wallets_coll.find_one({"user_id": user_id})
    if not wallet:
        # Auto-create if user is verified (failsafe backward compatibility)
        users_coll = get_users_collection()
        user = await users_coll.find_one({"_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id})
        if user and user.get("kyc_status") == "verified":
            wallet = await create_wallet(user_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found or user KYC is not verified"
            )
    return wallet


async def credit_pending(user_id: str, amount: float, payout_id: str, trigger_type: str) -> Dict[str, Any]:
    wallets_coll = get_wallets_collection()
    tx_coll = get_wallet_transactions_collection()
    
    wallet = await wallets_coll.find_one({"user_id": user_id})
    if not wallet:
        wallet = await create_wallet(user_id)
        
    if wallet.get("status") == "frozen":
        raise WalletError(f"Cannot credit frozen wallet for user {user_id}", "WALLET_FROZEN")
        
    now = datetime.utcnow()
    amount = float(amount)
    
    # Increment pending balance
    await wallets_coll.update_one(
        {"user_id": user_id},
        {
            "$inc": {"pending_balance": amount},
            "$set": {"updated_at": now}
        }
    )
    
    # Reload wallet for running balances
    wallet = await wallets_coll.find_one({"user_id": user_id})
    
    # Write Transaction Log (pending state)
    tx_doc = {
        "wallet_id": wallet["_id"],
        "user_id": user_id,
        "type": "credit_pending",
        "amount": amount,
        "running_available": float(wallet["available_balance"]),
        "running_pending": float(wallet["pending_balance"]),
        "reference_id": payout_id,
        "status": "pending",  # will become matured after 24h
        "description": f"Pending payout of ₹{amount} credited for trigger: {trigger_type}",
        "created_at": now
    }
    await tx_coll.insert_one(tx_doc)
    logger.info(f"Credited pending amount ₹{amount} to user {user_id}")
    return wallet


async def release_pending_balances() -> int:
    """
    Periodic job that releases pending payouts that have matured (>24 hours).
    """
    tx_coll = get_wallet_transactions_collection()
    wallets_coll = get_wallets_collection()
    
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    # Find all pending credits older than 24 hours
    pending_txs = await tx_coll.find({
        "type": "credit_pending",
        "status": "pending",
        "created_at": {"$lte": cutoff}
    }).to_list(length=None)
    
    if not pending_txs:
        return 0
        
    processed_count = 0
    for tx in pending_txs:
        user_id = tx["user_id"]
        amount = float(tx["amount"])
        
        wallet = await wallets_coll.find_one({"user_id": user_id})
        if not wallet or wallet.get("status") == "frozen":
            logger.warning(f"Skipping pending balance release for frozen/missing wallet for user {user_id}")
            continue
            
        now = datetime.utcnow()
        
        # Shift balances
        await wallets_coll.update_one(
            {"user_id": user_id},
            {
                "$inc": {
                    "pending_balance": -amount,
                    "available_balance": amount
                },
                "$set": {"updated_at": now}
            }
        )
        
        # Mark credit transaction as matured
        await tx_coll.update_one(
            {"_id": tx["_id"]},
            {"$set": {"status": "matured"}}
        )
        
        # Reload wallet for running balances
        wallet = await wallets_coll.find_one({"user_id": user_id})
        
        # Insert double-entry release log
        release_tx = {
            "wallet_id": wallet["_id"],
            "user_id": user_id,
            "type": "release_to_available",
            "amount": amount,
            "running_available": float(wallet["available_balance"]),
            "running_pending": float(wallet["pending_balance"]),
            "reference_id": str(tx["_id"]),
            "description": f"Matured pending balance of ₹{amount} moved to available",
            "created_at": now
        }
        await tx_coll.insert_one(release_tx)
        processed_count += 1
        logger.info(f"Released matured pending amount ₹{amount} for user {user_id}")
        
    return processed_count


async def request_withdrawal(user_id: str, amount: float, destination_details: Dict[str, Any]) -> Dict[str, Any]:
    wallets_coll = get_wallets_collection()
    tx_coll = get_wallet_transactions_collection()
    withdrawal_coll = get_withdrawal_requests_collection()
    
    wallet = await wallets_coll.find_one({"user_id": user_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
        
    if wallet.get("status") == "frozen":
        raise HTTPException(status_code=400, detail="Wallet is frozen")
        
    amount = float(amount)
    available = float(wallet["available_balance"])
    
    if available < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient available balance. Requested: ₹{amount}, Available: ₹{available}"
        )
        
    now = datetime.utcnow()
    
    # Auto-approve rule: withdrawals <= 10,000 are auto-approved
    is_auto_approved = amount <= 10000.0
    withdrawal_status = "approved" if is_auto_approved else "pending_approval"
    
    # Create withdrawal request record
    withdrawal_doc = {
        "user_id": user_id,
        "amount": amount,
        "status": withdrawal_status,
        "destination_details": destination_details,
        "razorpay_payout_id": None,
        "admin_reviewer_id": None,
        "rejection_reason": None,
        "created_at": now,
        "updated_at": now
    }
    result = await withdrawal_coll.insert_one(withdrawal_doc)
    withdrawal_id = str(result.inserted_id)
    
    # Deduct amount from available balance
    await wallets_coll.update_one(
        {"user_id": user_id},
        {
            "$inc": {"available_balance": -amount},
            "$set": {"updated_at": now}
        }
    )
    
    # Reload wallet for running balances
    wallet = await wallets_coll.find_one({"user_id": user_id})
    
    # Write Transaction Log (withdrawal hold/debit)
    tx_doc = {
        "wallet_id": wallet["_id"],
        "user_id": user_id,
        "type": "withdrawal_hold",
        "amount": amount,
        "running_available": float(wallet["available_balance"]),
        "running_pending": float(wallet["pending_balance"]),
        "reference_id": withdrawal_id,
        "description": f"Withdrawal request of ₹{amount} submitted. Status: {withdrawal_status}",
        "created_at": now
    }
    await tx_coll.insert_one(tx_doc)
    
    if is_auto_approved:
        # In a real integration, we would dispatch to Razorpay API here.
        # We will mock the payout processing and mark it completed.
        await withdrawal_coll.update_one(
            {"_id": ObjectId(withdrawal_id)},
            {
                "$set": {
                    "status": "completed",
                    "razorpay_payout_id": f"payout_auto_{withdrawal_id}",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Write withdrawal complete transaction
        complete_tx = {
            "wallet_id": wallet["_id"],
            "user_id": user_id,
            "type": "withdrawal_complete",
            "amount": amount,
            "running_available": float(wallet["available_balance"]),
            "running_pending": float(wallet["pending_balance"]),
            "reference_id": withdrawal_id,
            "description": f"Withdrawal request of ₹{amount} auto-approved and completed.",
            "created_at": datetime.utcnow()
        }
        await tx_coll.insert_one(complete_tx)
        logger.info(f"Auto-approved and processed withdrawal ₹{amount} for user {user_id}")
        
    return {
        "withdrawal_id": withdrawal_id,
        "status": withdrawal_status,
        "auto_approved": is_auto_approved,
        "message": "Withdrawal request processed." if is_auto_approved else "Withdrawal request pending admin approval."
    }


async def approve_withdrawal(withdrawal_id: str, admin_id: str) -> Dict[str, Any]:
    withdrawal_coll = get_withdrawal_requests_collection()
    wallets_coll = get_wallets_collection()
    tx_coll = get_wallet_transactions_collection()
    
    req = await withdrawal_coll.find_one({"_id": ObjectId(withdrawal_id)})
    if not req:
        raise HTTPException(status_code=404, detail="Withdrawal request not found")
        
    if req["status"] != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Request is in status: {req['status']}, cannot approve.")
        
    now = datetime.utcnow()
    user_id = req["user_id"]
    amount = float(req["amount"])
    
    await withdrawal_coll.update_one(
        {"_id": ObjectId(withdrawal_id)},
        {
            "$set": {
                "status": "completed",
                "admin_reviewer_id": admin_id,
                "razorpay_payout_id": f"payout_admin_{withdrawal_id}",
                "updated_at": now
            }
        }
    )
    
    wallet = await wallets_coll.find_one({"user_id": user_id})
    
    # Write Transaction Log (withdrawal complete)
    complete_tx = {
        "wallet_id": wallet["_id"],
        "user_id": user_id,
        "type": "withdrawal_complete",
        "amount": amount,
        "running_available": float(wallet["available_balance"]),
        "running_pending": float(wallet["pending_balance"]),
        "reference_id": withdrawal_id,
        "description": f"Withdrawal request of ₹{amount} approved by admin: {admin_id}.",
        "created_at": now
    }
    await tx_coll.insert_one(complete_tx)
    logger.info(f"Admin {admin_id} approved withdrawal {withdrawal_id} of ₹{amount}")
    return {"success": True, "message": "Withdrawal approved and processed."}


async def reject_withdrawal(withdrawal_id: str, admin_id: str, reason: str) -> Dict[str, Any]:
    withdrawal_coll = get_withdrawal_requests_collection()
    wallets_coll = get_wallets_collection()
    tx_coll = get_wallet_transactions_collection()
    
    req = await withdrawal_coll.find_one({"_id": ObjectId(withdrawal_id)})
    if not req:
        raise HTTPException(status_code=404, detail="Withdrawal request not found")
        
    if req["status"] != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Request is in status: {req['status']}, cannot reject.")
        
    now = datetime.utcnow()
    user_id = req["user_id"]
    amount = float(req["amount"])
    
    # Mark withdrawal request as rejected
    await withdrawal_coll.update_one(
        {"_id": ObjectId(withdrawal_id)},
        {
            "$set": {
                "status": "rejected",
                "admin_reviewer_id": admin_id,
                "rejection_reason": reason,
                "updated_at": now
            }
        }
    )
    
    # Refund amount back to available balance
    await wallets_coll.update_one(
        {"user_id": user_id},
        {
            "$inc": {"available_balance": amount},
            "$set": {"updated_at": now}
        }
    )
    
    wallet = await wallets_coll.find_one({"user_id": user_id})
    
    # Write Transaction Log (withdrawal refund)
    refund_tx = {
        "wallet_id": wallet["_id"],
        "user_id": user_id,
        "type": "withdrawal_refund",
        "amount": amount,
        "running_available": float(wallet["available_balance"]),
        "running_pending": float(wallet["pending_balance"]),
        "reference_id": withdrawal_id,
        "description": f"Withdrawal request of ₹{amount} rejected by admin: {admin_id}. Reason: {reason}.",
        "created_at": now
    }
    await tx_coll.insert_one(refund_tx)
    logger.info(f"Admin {admin_id} rejected withdrawal {withdrawal_id} of ₹{amount}. Refunded.")
    return {"success": True, "message": "Withdrawal rejected and funds refunded."}


async def freeze_wallet(user_id: str, freeze: bool) -> Dict[str, Any]:
    wallets_coll = get_wallets_collection()
    
    wallet = await wallets_coll.find_one({"user_id": user_id})
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
        
    status_str = "frozen" if freeze else "active"
    
    await wallets_coll.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "status": status_str,
                "updated_at": datetime.utcnow()
            }
        }
    )
    logger.info(f"Wallet for user {user_id} set to status: {status_str}")
    return {"success": True, "status": status_str}


async def get_wallet_analytics() -> Dict[str, Any]:
    wallets_coll = get_wallets_collection()
    withdrawal_coll = get_withdrawal_requests_collection()
    
    # Aggregate total available and pending balances
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_available": {"$sum": "$available_balance"},
                "total_pending": {"$sum": "$pending_balance"}
            }
        }
    ]
    balances_res = await wallets_coll.aggregate(pipeline).to_list(length=1)
    
    total_available = balances_res[0]["total_available"] if balances_res else 0.0
    total_pending = balances_res[0]["total_pending"] if balances_res else 0.0
    
    total_frozen = await wallets_coll.count_documents({"status": "frozen"})
    pending_approvals = await withdrawal_coll.count_documents({"status": "pending_approval"})
    
    return {
      "total_available_all_wallets": float(total_available),
      "total_pending_all_wallets": float(total_pending),
      "total_frozen_wallets": int(total_frozen),
      "pending_approvals_count": int(pending_approvals)
    }
