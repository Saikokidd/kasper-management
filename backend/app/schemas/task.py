from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.task import TaskType, TaskStatus
from app.schemas.user import UserOut

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: TaskType = TaskType.daily
    assigned_to_ids: List[int]  # мультиназначение
    due_date: Optional[datetime] = None

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
    assignees: List[UserOut]
    completion_comment: Optional[str]
    completion_media: Optional[str]

    class Config:
        from_attributes = True
