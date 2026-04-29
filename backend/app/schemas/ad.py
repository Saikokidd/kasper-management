from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.ad import AdPlatform
from app.schemas.user import UserOut

class AdCreate(BaseModel):
    platform: AdPlatform
    published_at: Optional[datetime] = None

class AdUpdate(BaseModel):
    published_at: Optional[datetime] = None

class AdOut(BaseModel):
    id: int
    created_at: datetime
    platform: AdPlatform
    published_at: Optional[datetime]
    created_by: UserOut

    class Config:
        from_attributes = True
