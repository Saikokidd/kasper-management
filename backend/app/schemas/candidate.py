from pydantic import BaseModel
from datetime import datetime
from typing import Any
from app.schemas.user import UserOut
from app.schemas.form_template import FormTemplateOut

class CandidateCreate(BaseModel):
    full_name: str
    template_id: int
    fields: dict[str, Any] = {}

class CandidateUpdate(BaseModel):
    full_name: str | None = None
    fields: dict[str, Any] | None = None

class CandidateOut(BaseModel):
    id: int
    full_name: str
    created_at: datetime
    template: FormTemplateOut
    fields: dict[str, Any]
    created_by: UserOut

    class Config:
        from_attributes = True
