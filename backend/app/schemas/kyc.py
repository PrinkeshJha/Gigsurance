from pydantic import BaseModel, Field
from typing import Optional

class KycSubmitRequest(BaseModel):
    document_type: str = Field(..., pattern="^(PAN|AADHAAR|DL)$", description="Type of ID document: PAN, AADHAAR, or DL")
    document_number: str = Field(..., min_length=5, max_length=20, description="The document number/ID")

class KycActionRequest(BaseModel):
    user_id: str
    action: str = Field(..., pattern="^(approve|reject)$", description="approve or reject")
    comments: Optional[str] = None
