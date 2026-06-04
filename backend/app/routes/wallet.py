import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from bson import ObjectId

from app.deps.auth import get_current_user, check_role, get_current_admin
from app.schemas.wallet import (
    WithdrawRequest,
    WalletResponse,
    WalletTransactionResponse,
    WithdrawalResponse,
    WalletAnalyticsResponse,
    WalletFreezeRequest
)
from app.services import wallet_service

logger = logging.getLogger("gigsurance-backend.wallet")

router = APIRouter(tags=["wallet"])

def format_wallet_doc(wallet: Dict[str, Any]) -> WalletResponse:
    return WalletResponse(
        user_id=str(wallet.get("user_id")),
        available_balance=float(wallet.get("available_balance", 0.0)),
        pending_balance=float(wallet.get("pending_balance", 0.0)),
        status=wallet.get("status", "active"),
        created_at=wallet.get("created_at"),
        updated_at=wallet.get("updated_at")
    )

def format_transaction_doc(tx: Dict[str, Any]) -> WalletTransactionResponse:
    return WalletTransactionResponse(
        id=str(tx.get("_id")),
        type=tx.get("type"),
        amount=float(tx.get("amount", 0.0)),
        running_available=float(tx.get("running_available", 0.0)),
        running_pending=float(tx.get("running_pending", 0.0)),
        reference_id=str(tx.get("reference_id")) if tx.get("reference_id") else None,
        description=tx.get("description"),
        created_at=tx.get("created_at")
    )

def format_withdrawal_doc(w: Dict[str, Any]) -> WithdrawalResponse:
    return WithdrawalResponse(
        id=str(w.get("_id")),
        user_id=str(w.get("user_id")),
        amount=float(w.get("amount", 0.0)),
        status=w.get("status"),
        destination_details=w.get("destination_details", {}),
        razorpay_payout_id=w.get("razorpay_payout_id"),
        admin_reviewer_id=w.get("admin_reviewer_id"),
        rejection_reason=w.get("rejection_reason"),
        created_at=w.get("created_at"),
        updated_at=w.get("updated_at")
    )


# ---------------------------------------------------------
# WORKER ENDPOINTS
# ---------------------------------------------------------

@router.get("/me", response_model=WalletResponse)
async def get_my_wallet(user: dict = Depends(get_current_user)):
    try:
        user_id = str(user["_id"])
        wallet = await wallet_service.get_wallet_by_user(user_id)
        return format_wallet_doc(wallet)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching wallet for user {user.get('_id')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wallet details"
        )


@router.get("/me/transactions", response_model=List[WalletTransactionResponse])
async def get_my_transactions(user: dict = Depends(get_current_user)):
    try:
        from app.db.database import get_wallet_transactions_collection
        tx_coll = get_wallet_transactions_collection()
        user_id = str(user["_id"])
        
        txs = await tx_coll.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return [format_transaction_doc(tx) for tx in txs]
    except Exception as e:
        logger.exception(f"Error fetching transactions for user {user.get('_id')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transaction logs"
        )


@router.post("/withdraw")
async def withdraw_funds(payload: WithdrawRequest, user: dict = Depends(get_current_user)):
    try:
        user_id = str(user["_id"])
        res = await wallet_service.request_withdrawal(user_id, payload.amount, payload.destination_details)
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error requesting withdrawal for user {user.get('_id')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process withdrawal request"
        )


@router.get("/me/withdrawals", response_model=List[WithdrawalResponse])
async def get_my_withdrawals(user: dict = Depends(get_current_user)):
    try:
        from app.db.database import get_withdrawal_requests_collection
        withdrawal_coll = get_withdrawal_requests_collection()
        user_id = str(user["_id"])
        
        requests = await withdrawal_coll.find({"user_id": user_id}).sort("created_at", -1).to_list(length=None)
        return [format_withdrawal_doc(w) for w in requests]
    except Exception as e:
        logger.exception(f"Error fetching withdrawal requests for user {user.get('_id')}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch withdrawal requests"
        )


# ---------------------------------------------------------
# ADMIN / AUDITOR ENDPOINTS
# ---------------------------------------------------------

@router.get("/admin/wallets", response_model=List[WalletResponse])
async def list_all_wallets(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    try:
        from app.db.database import get_wallets_collection
        wallets_coll = get_wallets_collection()
        wallets = await wallets_coll.find({}).to_list(length=None)
        return [format_wallet_doc(w) for w in wallets]
    except Exception as e:
        logger.exception("Error listing wallets for admin")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list wallets"
        )


@router.get("/admin/withdrawals", response_model=List[WithdrawalResponse])
async def list_pending_withdrawals(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    try:
        from app.db.database import get_withdrawal_requests_collection
        withdrawal_coll = get_withdrawal_requests_collection()
        requests = await withdrawal_coll.find({"status": "pending_approval"}).sort("created_at", -1).to_list(length=None)
        return [format_withdrawal_doc(w) for w in requests]
    except Exception as e:
        logger.exception("Error listing withdrawal requests for admin")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list withdrawal requests"
        )


@router.patch("/admin/withdrawals/{id}/approve")
async def approve_withdrawal_request(id: str, admin: dict = Depends(check_role(["admin", "ops"]))):
    try:
        admin_id = str(admin.get("_id", "admin_system"))
        res = await wallet_service.approve_withdrawal(id, admin_id)
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error approving withdrawal request {id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve withdrawal"
        )


@router.patch("/admin/withdrawals/{id}/reject")
async def reject_withdrawal_request(id: str, reason: Dict[str, str], admin: dict = Depends(check_role(["admin", "ops"]))):
    try:
        admin_id = str(admin.get("_id", "admin_system"))
        reject_reason = reason.get("reason", "Rejected by administrator")
        res = await wallet_service.reject_withdrawal(id, admin_id, reject_reason)
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error rejecting withdrawal request {id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject withdrawal"
        )


@router.post("/admin/wallets/{worker_id}/freeze")
async def freeze_worker_wallet(worker_id: str, payload: WalletFreezeRequest, admin: dict = Depends(check_role(["admin", "ops"]))):
    try:
        res = await wallet_service.freeze_wallet(worker_id, payload.freeze)
        return res
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error changing freeze status of wallet for user {worker_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to modify wallet freeze status"
        )


@router.get("/admin/analytics", response_model=WalletAnalyticsResponse)
async def get_wallets_analytics_data(admin: dict = Depends(check_role(["admin", "ops", "auditor", "claims_agent"]))):
    try:
        res = await wallet_service.get_wallet_analytics()
        return res
    except Exception as e:
        logger.exception("Error getting wallet analytics data")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallet analytics"
        )
