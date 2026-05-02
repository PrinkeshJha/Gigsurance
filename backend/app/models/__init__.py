from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema


class User(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: str
    password_hash: str
    name: str
    phone: Optional[str] = None
    city: str
    zone: str
    platform: str
    working_hours: str  # "HH:MM-HH:MM"
    risk_score: float
    is_onboarded: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Policy(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    status: str  # "active" | "paused"
    weekly_premium: float
    risk_score: float
    coverage: list[str]  # ["heat", "rain", "civil"]
    weekly_cap: float
    per_delivery_deduction: float
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Subscription(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    policy_id: PyObjectId
    week_start: datetime  # Monday of current week
    total_deducted_this_week: float = 0.0
    deliveries_count: int = 0
    cap_reached: bool = False
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TriggerLog(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    city: str
    trigger_type: str  # "heat" | "rain" | "civil"
    trigger_value: Optional[float] = None
    news_headline: Optional[str] = None
    timestamp: datetime
    status: str  # "active" | "resolved"

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Payout(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    policy_id: PyObjectId
    trigger_log_id: PyObjectId
    amount: float
    trigger_type: str  # "heat" | "rain" | "civil"
    status: str  # "credited" | "pending" | "failed"
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Notification(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    message: str
    type: str  # "payout" | "trigger" | "premium_update" | "system"
    read: bool = False
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}