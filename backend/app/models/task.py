from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class TaskType(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class TaskStatus(str, enum.Enum):
    pending = "pending"
    done = "done"

class TaskTemplate(Base):
    __tablename__ = "task_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_id])

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    type = Column(Enum(TaskType), nullable=False, default=TaskType.daily)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.pending)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_id])

    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])

    template_id = Column(Integer, ForeignKey("task_templates.id"), nullable=True)
    template = relationship("TaskTemplate")

    completion_comment = Column(Text, nullable=True)
    media_url = Column(String, nullable=True)
