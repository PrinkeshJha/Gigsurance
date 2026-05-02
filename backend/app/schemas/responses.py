from pydantic import BaseModel
from typing import List, Dict

class WeatherResponse(BaseModel):
    temperature: float
    condition: str
    zone: str
    risk_level: str

class TriggerResponse(BaseModel):
    id: str
    type: str
    zone: str
    severity: str
    timestamp: str

class TransactionResponse(BaseModel):
    id: str
    amount: float
    type: str
    status: str
    created_at: str

class AnalyticsResponse(BaseModel):
    total_users: int
    active_policies: int
    total_payouts: float
    risk_distribution: Dict[str, int]

class AdminKPIsResponse(BaseModel):
    revenue: float
    active_users: int
    claims_processed: int
    growth_rate: float