from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut

class InterviewCreate(BaseModel):
    full_name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    comment: Optional[str] = None

class InterviewUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    comment: Optional[str] = None

class InterviewOut(BaseModel):
    id: int
    created_at: datetime
    scheduled_at: Optional[datetime]
    full_name: str
    username: Optional[str]
    phone: Optional[str]
    comment: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True
