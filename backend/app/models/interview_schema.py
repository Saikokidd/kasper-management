from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut

class InterviewCreate(BaseModel):
    full_name: str
    username: Optional[str] = None       # Telegram
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    phone: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    comment: Optional[str] = None
    result: Optional[str] = None
    status: str = 'scheduled'

class InterviewUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    instagram: Optional[str] = None
    tiktok: Optional[str] = None
    phone: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    comment: Optional[str] = None
    result: Optional[str] = None
    status: Optional[str] = None
    photo_path: Optional[str] = None

class InterviewOut(BaseModel):
    id: int
    created_at: datetime
    scheduled_at: Optional[datetime]
    status: str
    full_name: str
    username: Optional[str]
    instagram: Optional[str]
    tiktok: Optional[str]
    phone: Optional[str]
    comment: Optional[str]
    result: Optional[str]
    photo_path: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True