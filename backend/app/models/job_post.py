from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class JobPlatform(str, enum.Enum):
    olx = "olx"
    workua = "workua"

class JobPostStatus(str, enum.Enum):
    active = "active"
    blocked = "blocked"

class JobPost(Base):
    __tablename__ = "job_posts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    platform = Column(Enum(JobPlatform), nullable=False)
    content = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    responses = Column(Integer, default=0)
    comment = Column(Text, nullable=True)
    status = Column(Enum(JobPostStatus), nullable=False, default=JobPostStatus.active)
    block_reason = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
