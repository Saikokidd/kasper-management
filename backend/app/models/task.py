from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Table
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

# Таблица мультиназначений
task_assignments = Table(
    'task_assignments',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)

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

    # Мультиназначение
    assignees = relationship("User", secondary=task_assignments, lazy="joined")

    completion_comment = Column(Text, nullable=True)
    completion_media = Column(String(500), nullable=True)
