from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional

class Settings(BaseSettings):
    # ===============================
    # CORE
    # ===============================
    mongo_uri: str
    db_name: str = "gigsurance"


    # ===============================
    # AUTH / JWT
    # ===============================
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    # ===============================
    # EXTERNAL APIs
    # ===============================
    openweather_api_key: Optional[str] = None
    newsapi_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # ===============================
    # PAYMENTS (RAZORPAY)
    # ===============================
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None

    # ===============================
    # ENVIRONMENT
    # ===============================
    debug: bool = False

    # ===============================
    # SETTINGS CONFIG
    # ===============================
    model_config = SettingsConfigDict(
        env_file=".env",              # works in dev
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # ===============================
    # VALIDATIONS
    # ===============================

    @field_validator("mongo_uri")
    @classmethod
    def validate_mongo(cls, v: str):
        if not v.startswith("mongodb"):
            raise ValueError("❌ Invalid Mongo URI")
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt(cls, v: str):
        if not v or len(v) < 12:
            raise ValueError("❌ JWT_SECRET must be at least 12 characters")
        return v

    @field_validator("jwt_exp_minutes")
    @classmethod
    def validate_expiry(cls, v: int):
        if v <= 0:
            raise ValueError("❌ JWT_EXP_MINUTES must be positive")
        return v

    @field_validator("razorpay_key_secret")
    @classmethod
    def validate_razorpay(cls, v, values):
        key_id = values.data.get("razorpay_key_id")

        # If one exists, both must exist
        if key_id and not v:
            raise ValueError("❌ RAZORPAY_KEY_SECRET missing")

        return v


# ===============================

# SINGLETON INSTANCE

# ===============================

settings = Settings()
