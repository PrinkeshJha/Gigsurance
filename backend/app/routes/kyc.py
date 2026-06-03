import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from typing import List, Dict, Any

from app.db.database import (
    get_users_collection,
    get_policies_collection,
    get_kyc_logs_collection,
    get_notifications_collection,
    get_payouts_collection
)
from app.deps.auth import get_current_user, check_role
from app.schemas.kyc import KycSubmitRequest, KycActionRequest
from app.routes.auth import format_user_response

logger = logging.getLogger("gigsurance-backend.kyc")

router = APIRouter(tags=["kyc"])

# Helper to mask document number
def mask_document_number(doc_num: str) -> str:
    cleaned = doc_num.strip()
    if len(cleaned) <= 4:
        return cleaned
    return "X" * (len(cleaned) - 4) + cleaned[-4:]


# -------------------------------
# RELEASE PENDING KYC PAYOUTS
# -------------------------------
async def release_pending_kyc_payouts(user_id_str: str):
    try:
        payouts_collection = get_payouts_collection()
        notifications_collection = get_notifications_collection()
        now = datetime.utcnow()

        pending_payouts = await payouts_collection.find({
            "user_id": {"$in": [user_id_str, ObjectId(user_id_str)]} if ObjectId.is_valid(user_id_str) else user_id_str,
            "status": "pending_kyc"
        }).to_list(length=None)

        for payout in pending_payouts:
            await payouts_collection.update_one(
                {"_id": payout["_id"]},
                {"$set": {"status": "credited", "updated_at": now}}
            )

            await notifications_collection.insert_one({
                "user_id": user_id_str,
                "message": f"₹{payout['amount']} credited for past trigger {payout.get('trigger_type')} after successful KYC verification.",
                "type": "payout",
                "read": False,
                "created_at": now
            })
    except Exception as e:
        logger.error(f"Failed to release pending KYC payouts for user {user_id_str}: {e}")


# -------------------------------
# SUBMIT KYC
# -------------------------------
@router.post("/submit")
async def submit_kyc(payload: KycSubmitRequest, user: dict = Depends(get_current_user)):
    try:
        users_collection = get_users_collection()
        policies_collection = get_policies_collection()
        kyc_logs_collection = get_kyc_logs_collection()
        notifications_collection = get_notifications_collection()

        user_id = user["_id"]
        user_id_str = str(user_id)

        current_status = user.get("kyc_status", "uninitiated")
        if current_status == "verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="KYC is already verified."
            )

        doc_type = payload.document_type.upper()
        doc_num = payload.document_number.strip()
        masked_ref = mask_document_number(doc_num)

        # Mock Auto-approval check: ends with a digit (0-9)
        is_auto_approved = doc_num[-1].isdigit() if doc_num else False

        now = datetime.utcnow()

        if is_auto_approved:
            # Auto approve
            await users_collection.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "kyc_status": "verified",
                        "kyc_verified_at": now,
                        "kyc_document_type": doc_type,
                        "kyc_document_ref": masked_ref
                    }
                }
            )

            # Activate policy if pending_kyc
            await policies_collection.update_one(
                {"user_id": user_id_str, "status": "pending_kyc"},
                {"$set": {"status": "active", "updated_at": now}}
            )

            # Log
            await kyc_logs_collection.insert_one({
                "user_id": user_id_str,
                "action": "auto_approve",
                "status": "verified",
                "document_type": doc_type,
                "document_ref": masked_ref,
                "comments": "Automatically verified via mock compliance provider API.",
                "created_at": now
            })

            # Notify
            await notifications_collection.insert_one({
                "user_id": user_id_str,
                "message": "Your KYC has been automatically verified successfully.",
                "type": "kyc",
                "read": False,
                "created_at": now
            })

            await release_pending_kyc_payouts(user_id_str)

            updated_user = await users_collection.find_one({"_id": user_id})
            return {
                "success": True,
                "message": "KYC verified automatically.",
                "user": format_user_response(updated_user)
            }
        else:
            # Manual review pending
            await users_collection.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "kyc_status": "pending",
                        "kyc_document_type": doc_type,
                        "kyc_document_ref": masked_ref
                    }
                }
            )

            # Log
            await kyc_logs_collection.insert_one({
                "user_id": user_id_str,
                "action": "submit",
                "status": "pending",
                "document_type": doc_type,
                "document_ref": masked_ref,
                "comments": "Submitted for manual review.",
                "created_at": now
            })

            # Notify
            await notifications_collection.insert_one({
                "user_id": user_id_str,
                "message": "Your KYC document has been received and is pending review.",
                "type": "kyc",
                "read": False,
                "created_at": now
            })

            updated_user = await users_collection.find_one({"_id": user_id})
            return {
                "success": True,
                "message": "KYC submitted and pending review.",
                "user": format_user_response(updated_user)
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ KYC submission failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit KYC data."
        )


# -------------------------------
# GET KYC STATUS
# -------------------------------
@router.get("/status")
async def get_kyc_status(user: dict = Depends(get_current_user)):
    try:
        kyc_logs_collection = get_kyc_logs_collection()
        user_id_str = str(user["_id"])

        logs = await kyc_logs_collection.find(
            {"user_id": user_id_str}
        ).sort("created_at", -1).to_list(length=None)

        formatted_logs = [
            {
                "id": str(log["_id"]),
                "action": log.get("action"),
                "status": log.get("status"),
                "document_type": log.get("document_type"),
                "document_ref": log.get("document_ref"),
                "comments": log.get("comments"),
                "created_at": log["created_at"].isoformat() if log.get("created_at") else None
            }
            for log in logs
        ]

        return {
            "kyc_status": user.get("kyc_status", "uninitiated"),
            "kyc_verified_at": user.get("kyc_verified_at").isoformat() if user.get("kyc_verified_at") else None,
            "kyc_document_type": user.get("kyc_document_type"),
            "kyc_document_ref": user.get("kyc_document_ref"),
            "history": formatted_logs
        }
    except Exception as e:
        logger.exception("❌ Failed to fetch KYC status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch KYC status."
        )


# -------------------------------
# GET PENDING KYC (ADMIN/OPS/CLAIMS)
# -------------------------------
@router.get("/admin/pending")
async def get_pending_kyc(admin: dict = Depends(check_role(["admin", "ops", "claims_agent"]))):
    try:
        users_collection = get_users_collection()
        pending_users = await users_collection.find({"kyc_status": "pending"}).to_list(length=None)
        return [format_user_response(u) for u in pending_users]
    except Exception as e:
        logger.exception("❌ Failed to fetch pending KYC list")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending KYC list."
        )


# -------------------------------
# KYC ACTION (ADMIN/OPS/CLAIMS)
# -------------------------------
@router.post("/admin/action")
async def kyc_action(payload: KycActionRequest, admin: dict = Depends(check_role(["admin", "ops", "claims_agent"]))):
    try:
        users_collection = get_users_collection()
        policies_collection = get_policies_collection()
        kyc_logs_collection = get_kyc_logs_collection()
        notifications_collection = get_notifications_collection()

        target_user_id_str = payload.user_id
        try:
            target_user_id = ObjectId(target_user_id_str)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format."
            )

        user = await users_collection.find_one({"_id": target_user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        now = datetime.utcnow()

        if payload.action == "approve":
            await users_collection.update_one(
                {"_id": target_user_id},
                {
                    "$set": {
                        "kyc_status": "verified",
                        "kyc_verified_at": now
                    }
                }
            )

            # Activate policy if pending_kyc
            await policies_collection.update_one(
                {"user_id": target_user_id_str, "status": "pending_kyc"},
                {"$set": {"status": "active", "updated_at": now}}
            )

            # Log
            await kyc_logs_collection.insert_one({
                "user_id": target_user_id_str,
                "action": "admin_approve",
                "status": "verified",
                "comments": payload.comments or "Approved by admin/ops.",
                "created_at": now
            })

            # Notify
            await notifications_collection.insert_one({
                "user_id": target_user_id_str,
                "message": "Your KYC has been approved by our admin team.",
                "type": "kyc",
                "read": False,
                "created_at": now
            })

            await release_pending_kyc_payouts(target_user_id_str)

            return {"success": True, "message": "KYC approved and policy activated."}

        elif payload.action == "reject":
            await users_collection.update_one(
                {"_id": target_user_id},
                {
                    "$set": {
                        "kyc_status": "failed"
                    }
                }
            )

            # Log
            await kyc_logs_collection.insert_one({
                "user_id": target_user_id_str,
                "action": "admin_reject",
                "status": "failed",
                "comments": payload.comments or "Rejected by admin/ops.",
                "created_at": now
            })

            # Notify
            await notifications_collection.insert_one({
                "user_id": target_user_id_str,
                "message": f"Your KYC has been rejected. Reason: {payload.comments or 'Incomplete or unreadable documents'}.",
                "type": "kyc",
                "read": False,
                "created_at": now
            })

            return {"success": True, "message": "KYC rejected."}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Failed to process KYC action")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record KYC action."
        )
