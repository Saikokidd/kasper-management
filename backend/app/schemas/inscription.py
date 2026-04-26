from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.inscription import InscriptionSource
from app.schemas.user import UserOut

class InscriptionCreate(BaseModel):
    full_name: str
    username: Optional[str] = None
    phone: Optional[str] = None
    source: InscriptionSource = InscriptionSource.self
    referred_by_id: Optional[int] = None
    comment: Optional[str] = None

class InscriptionUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[InscriptionSource] = None
    referred_by_id: Optional[int] = None
    comment: Optional[str] = None

class InscriptionOut(BaseModel):
    id: int
    created_at: datetime
    full_name: str
    username: Optional[str]
    phone: Optional[str]
    source: InscriptionSource
    referred_by: Optional[UserOut]
    comment: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True
