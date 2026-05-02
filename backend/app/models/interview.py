from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_at = Column(DateTime(timezone=True), nullable=True)

    # Статус: scheduled | completed
    status = Column(String(20), default='scheduled', nullable=False)

    full_name = Column(String, nullable=False)
    username = Column(String, nullable=True)      # Telegram
    instagram = Column(String, nullable=True)
    tiktok = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    result = Column(Text, nullable=True)          # Итог (только для completed)
    photo_path = Column(String(500), nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")