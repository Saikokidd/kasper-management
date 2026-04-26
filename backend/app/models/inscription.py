from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class InscriptionSource(str, enum.Enum):
    self = "self"
    referral = "referral"

class Inscription(Base):
    __tablename__ = "inscriptions"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    full_name = Column(String, nullable=False)
    username = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    source = Column(Enum(InscriptionSource), nullable=False, default=InscriptionSource.self)
    referred_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    referred_by = relationship("User", foreign_keys=[referred_by_id])

    comment = Column(Text, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", foreign_keys=[created_by_id])
