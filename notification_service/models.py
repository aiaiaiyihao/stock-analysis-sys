from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    condition = Column(String(20), nullable=False)
    threshold = Column(Float, nullable=False)
    message = Column(Text, nullable=False)
    event_timestamp = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

