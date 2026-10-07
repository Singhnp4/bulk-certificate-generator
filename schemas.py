from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class RecipientCreate(BaseModel):
    name: str
    email: EmailStr

class JobCreate(BaseModel):
    recipients: List[RecipientCreate]

class CertificateResponse(BaseModel):
    id: int
    recipient_name: str
    recipient_email: str
    status: str
    error_message: Optional[str] = None
    file_path: Optional[str] = None
    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: int
    status: str
    created_at: datetime
    certificates: List[CertificateResponse] = []
    class Config:
        from_attributes = True