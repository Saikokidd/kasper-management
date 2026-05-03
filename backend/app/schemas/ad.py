from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.ad import AdPlatform
from app.schemas.user import UserOut

class AdCreate(BaseModel):
    platform: AdPlatform
    published_at: Optional[datetime] = None
    description: Optional[str] = None

class AdUpdate(BaseModel):
    published_at: Optional[datetime] = None
    description: Optional[str] = None

class AdOut(BaseModel):
    id: int
    created_at: datetime
    platform: AdPlatform
    published_at: Optional[datetime]
    description: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True
