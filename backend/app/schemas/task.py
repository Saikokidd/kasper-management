from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.task import TaskType, TaskStatus
from app.schemas.user import UserOut

class TaskTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TaskTemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: TaskType = TaskType.daily
    assigned_to_id: int
    due_date: Optional[datetime] = None
    template_id: Optional[int] = None

class TaskComplete(BaseModel):
    completion_comment: Optional[str] = None

class TaskOut(BaseModel):
    id: int
    created_at: datetime
    due_date: Optional[datetime]
    title: str
    description: Optional[str]
    type: TaskType
    status: TaskStatus
    created_by: UserOut
    assigned_to: UserOut
    template: Optional[TaskTemplateOut]
    completion_comment: Optional[str]
    media_url: Optional[str]

    class Config:
        from_attributes = True
