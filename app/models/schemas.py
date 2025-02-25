from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ScanResponse(BaseModel):
    """Schema for scan response"""
    scan_id: str
    detected_language: str
    raw_text: str = Field(default="", description="Raw extracted OCR text")
    id_number: Optional[str] = Field(default=None, description="ID card number")
    name: Optional[str] = Field(default=None, description="Full name on ID")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth")
    address: Optional[str] = Field(default=None, description="Address")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional extracted data")