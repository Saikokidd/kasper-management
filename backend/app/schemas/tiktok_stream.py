from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut

class TiktokStreamCreate(BaseModel):
    stream_date: datetime
    views: int = 0
    subscriptions: int = 0
    inquiries: int = 0

class TiktokStreamUpdate(BaseModel):
    stream_date: Optional[datetime] = None
    views: Optional[int] = None
    subscriptions: Optional[int] = None
    inquiries: Optional[int] = None

class TiktokStreamOut(BaseModel):
    id: int
    created_at: datetime
    stream_date: datetime
    views: int
    subscriptions: int
    inquiries: int
    created_by: UserOut

    class Config:
        from_attributes = True
