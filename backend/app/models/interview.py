from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_at = Column(DateTime(timezone=True), nullable=True)

    full_name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    comment = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
