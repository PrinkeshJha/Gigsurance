from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class Location(BaseModel):
    lat: float
    lon: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class UserInDB(BaseModel):
    id: str | None = Field(None, alias="_id")
    name: str
    email: EmailStr
    mobile: str
    pan: str
    hashed_password: str
    platform: str
    zone: str | None = ""
    working_hours: str | None = ""
    role: str = "user"
    is_onboarded: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    location: Location | None = None
    hourly_rate: float = 0.0
    working_hours_per_day: int = 0
    weekly_cap: float = 0.0

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
