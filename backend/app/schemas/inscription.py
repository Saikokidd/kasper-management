from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.user import UserOut

class InscriptionCreate(BaseModel):
    full_name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    social_network: Optional[str] = None
    source_text: Optional[str] = None
    referred_by_id: Optional[int] = None
    comment: Optional[str] = None

class InscriptionUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    social_network: Optional[str] = None
    source_text: Optional[str] = None
    referred_by_id: Optional[int] = None
    comment: Optional[str] = None

class InscriptionOut(BaseModel):
    id: int
    created_at: datetime
    full_name: str
    username: Optional[str]
    phone: Optional[str]
    social_network: Optional[str]
    source_text: Optional[str]
    referred_by: Optional[UserOut]
    comment: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True
