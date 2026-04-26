from pydantic import BaseModel
from typing import List, Any
from app.schemas.user import UserOut

class FieldSchema(BaseModel):
    key: str
    label: str
    type: str = "text"  # text | textarea | date | select
    options: List[str] = []
    required: bool = False

class FormTemplateCreate(BaseModel):
    name: str
    fields: List[FieldSchema]

class FormTemplateUpdate(BaseModel):
    name: str | None = None
    fields: List[FieldSchema] | None = None

class FormTemplateOut(BaseModel):
    id: int
    name: str
    fields: List[Any]
    created_by: UserOut

    class Config:
        from_attributes = True
