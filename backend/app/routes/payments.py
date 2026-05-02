import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import razorpay
from typing import Dict, Any
from datetime import datetime

from app.config import settings
from app.deps.auth import get_current_user
import app.db.database as database

logger = logging.getLogger("gigsurance-backend")

router = APIRouter(tags=["payments"])


print("🔥 PAYMENTS ROUTE LOADED")

# -------------------------------

# 🔍 RAZORPAY DEBUG (FINAL)

# -------------------------------


print("========== RAZORPAY DEBUG ==========")
print("KEY ID:", settings.razorpay_key_id)
print("KEY SECRET:", settings.razorpay_key_secret)
print("KEY ID LENGTH:", len(settings.razorpay_key_id or ""))
print("KEY SECRET LENGTH:", len(settings.razorpay_key_secret or ""))
print("===================================")

# -------------------------------

# INIT RAZORPAY CLIENT

# -------------------------------

razorpay_client = None

if settings.razorpay_key_id and settings.razorpay_key_secret:
    razorpay_client = razorpay.Client(
        auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
    )
    logger.info("✅ Razorpay initialized")
else:
    logger.warning("⚠️ Razorpay keys missing — payments disabled")

# -------------------------------

# SCHEMAS

# -------------------------------

class OrderCreateRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in INR")
    currency: str = "INR"

class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

# -------------------------------

# CREATE ORDER

# -------------------------------

@router.post("/create-order")
async def create_order(
    request: OrderCreateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    if not razorpay_client:
        raise HTTPException(
            status_code=500,
            detail="Payment gateway not configured"
        )

    try:
        user_id = str(user.get("_id"))

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user"
            )

        # ✅ SAFE AMOUNT CONVERSION
        amount_paise = int(request.amount) * 100

        order_data = {
            "amount": amount_paise,
            "currency": request.currency,
            "receipt": f"rcpt_{user_id[-10:]}_{int(datetime.utcnow().timestamp())}",
            "payment_capture": 1,
            "notes": {
                "user_id": user_id
            }
        }

        logger.info(f"📦 Creating Razorpay order: {order_data}")

        order = razorpay_client.order.create(data=order_data)

        logger.info(f"✅ Razorpay order created: {order}")

        return {
            "order_id": order["id"],   # ✅ FIXED KEY NAME
            "amount": order["amount"],
            "currency": order["currency"],
            "key": settings.razorpay_key_id  # ✅ REQUIRED FOR FRONTEND
        }

    except Exception as e:
        logger.exception("❌ Razorpay order creation failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Razorpay error: {str(e)}"
        )

# -------------------------------

# VERIFY PAYMENT

# -------------------------------

@router.post("/verify")
async def verify_payment(
    request: PaymentVerifyRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    if not razorpay_client:
        raise HTTPException(
            status_code=500,
            detail="Payment gateway not configured"
        )

    try:
        user_id = str(user.get("_id"))

        params_dict = {
            "razorpay_order_id": request.razorpay_order_id,
            "razorpay_payment_id": request.razorpay_payment_id,
            "razorpay_signature": request.razorpay_signature
        }

        # ✅ VERIFY SIGNATURE
        razorpay_client.utility.verify_payment_signature(params_dict)

        # -------------------------------
        # SAVE PAYMENT
        # -------------------------------
        if database.payouts_collection is not None:
            await database.payouts_collection.insert_one({
                "user_id": user_id,
                "order_id": request.razorpay_order_id,
                "payment_id": request.razorpay_payment_id,
                "amount": None,
                "status": "success",
                "created_at": datetime.utcnow()
            })

        logger.info(f"✅ Payment verified: {request.razorpay_payment_id}")

        return {
            "status": "success",
            "message": "Payment verified successfully"
        }

    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment signature"
        )

    except Exception as e:
        logger.exception("❌ Payment verification failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment verification failed: {str(e)}"
        )
