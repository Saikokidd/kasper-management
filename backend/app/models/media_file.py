from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True, index=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_by = relationship("User")

    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)

    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    available = Column(Boolean, default=True)
