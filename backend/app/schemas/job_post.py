from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.job_post import JobPlatform, JobPostStatus
from app.schemas.user import UserOut

class JobPostCreate(BaseModel):
    platform: JobPlatform
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    responses: int = 0
    comment: Optional[str] = None
    status: JobPostStatus = JobPostStatus.active
    block_reason: Optional[str] = None

class JobPostUpdate(BaseModel):
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    responses: Optional[int] = None
    comment: Optional[str] = None
    status: Optional[JobPostStatus] = None
    block_reason: Optional[str] = None

class JobPostOut(BaseModel):
    id: int
    created_at: datetime
    platform: JobPlatform
    content: Optional[str]
    published_at: Optional[datetime]
    responses: int
    comment: Optional[str]
    status: JobPostStatus
    block_reason: Optional[str]
    created_by: UserOut

    class Config:
        from_attributes = True
