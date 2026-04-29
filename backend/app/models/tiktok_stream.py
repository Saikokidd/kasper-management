from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class TiktokStream(Base):
    __tablename__ = "tiktok_streams"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    stream_date = Column(DateTime(timezone=True), nullable=False)
    views = Column(Integer, nullable=False, default=0)
    subscriptions = Column(Integer, nullable=False, default=0)
    inquiries = Column(Integer, nullable=False, default=0)

    # Зарезервировано для TikTok API
    # tiktok_video_id = Column(String, nullable=True)
    # likes = Column(Integer, nullable=True)
    # shares = Column(Integer, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User")
