from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserOut

class MediaFileOut(BaseModel):
    id: int
    uploaded_at: datetime
    uploaded_by: UserOut
    entity_type: str
    entity_id: int
    filename: str
    size: int
    available: bool

    class Config:
        from_attributes = True
