from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class WithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0.0, description="Amount to withdraw")
    destination_details: Dict[str, Any] = Field(..., description="Bank details or UPI ID")

class WalletResponse(BaseModel):
    user_id: str
    available_balance: float
    pending_balance: float
    status: str
    created_at: datetime
    updated_at: datetime

class WalletTransactionResponse(BaseModel):
    id: str
    type: str
    amount: float
    running_available: float
    running_pending: float
    reference_id: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

class WithdrawalResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    status: str
    destination_details: Dict[str, Any]
    razorpay_payout_id: Optional[str] = None
    admin_reviewer_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class WalletAnalyticsResponse(BaseModel):
    total_available_all_wallets: float
    total_pending_all_wallets: float
    total_frozen_wallets: int
    pending_approvals_count: int

class WalletFreezeRequest(BaseModel):
    freeze: bool = Field(..., description="True to freeze the wallet, False to unfreeze")
